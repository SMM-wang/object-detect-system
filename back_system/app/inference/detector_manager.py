import threading
from pathlib import Path

from app.errors import DetectorBusyError, InferenceError, ValidationError
from app.inference.yolo_detector import YOLODetector


class DetectorManager:
    def __init__(self, config):
        self.config = config
        self.detectors = {}
        self.semaphore = threading.BoundedSemaphore(config["DETECTOR_MAX_CONCURRENCY"])
        self.acquire_timeout = config["DETECTOR_ACQUIRE_TIMEOUT_SECONDS"]
        self.initialized = False

    def initialize(self):
        model_paths = self._discover_models()
        if not model_paths:
            raise InferenceError("未找到可用 ONNX 模型")
        for model_path in model_paths:
            detector = YOLODetector(
                model_path=model_path,
                backend=self.config["MODEL_BACKEND"],
                allow_mock=self.config["ALLOW_MOCK_DETECTOR"],
            )
            detector.load()
            detector.warmup()
            self.detectors[model_path.name] = detector
        self.initialized = True

    def list_models(self):
        return [{"label": name, "value": name} for name in sorted(self.detectors)]

    def detect_image(self, image, confidence, iou, model_version=None):
        if not self.initialized:
            raise InferenceError("推理服务未初始化")
        detector = self._get_detector(model_version)
        acquired = self.semaphore.acquire(timeout=self.acquire_timeout)
        if not acquired:
            raise DetectorBusyError()
        try:
            return detector.detect(image, confidence, iou)
        except MemoryError as exc:
            raise DetectorBusyError("显存资源不足，请稍后重试") from exc
        except Exception as exc:
            raise InferenceError() from exc
        finally:
            self.semaphore.release()

    def _discover_models(self):
        model_dir = Path(self.config["MODEL_DIR"])
        model_paths = sorted(model_dir.glob("*.onnx")) if model_dir.exists() else []
        if model_paths:
            return model_paths
        fallback = Path(self.config["MODEL_PATH"])
        return [fallback] if fallback.exists() else []

    def _get_detector(self, model_version):
        if not model_version:
            raise ValidationError("modelVersion 为必填参数")
        detector = self.detectors.get(model_version)
        if detector is None:
            raise ValidationError(f"模型不存在: {model_version}")
        return detector
