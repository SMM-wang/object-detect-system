import ast
import json
import logging
from pathlib import Path

import cv2
import numpy as np


logger = logging.getLogger(__name__)


class YOLODetector:
    def __init__(self, model_path, backend="onnx", allow_mock=True):
        self.model_path = Path(model_path)
        self.backend = backend
        self.allow_mock = allow_mock
        self.mock = True
        self.session = None
        self.input_name = None
        self.output_names = None
        self.class_names = []
        self.providers = []

    def load(self):
        if not self.model_path.exists():
            if self.allow_mock:
                self.mock = True
                return
            raise FileNotFoundError(f"模型文件不存在: {self.model_path}")

        if self.backend != "onnx":
            if self.allow_mock:
                self.mock = True
                return
            raise RuntimeError(f"暂不支持的推理后端: {self.backend}")

        try:
            import onnxruntime as ort
        except ImportError as exc:
            if self.allow_mock:
                self.mock = True
                return
            raise RuntimeError("未安装 onnxruntime") from exc

        self.session = ort.InferenceSession(
            str(self.model_path),
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        self.providers = self.session.get_providers()
        logger.info("ONNX Runtime execution providers: %s", self.providers)
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [item.name for item in self.session.get_outputs()]
        self.class_names = self._load_class_names()
        self.mock = False

    def warmup(self):
        return self.detect(self._blank_image(640, 640), 0.25, 0.45)

    def detect(self, image, confidence, iou):
        if self.mock:
            return self._mock_detect(image, confidence)
        return self._detect_onnx(image, confidence, iou)

    def _detect_onnx(self, image, confidence, iou):
        blob, ratio, pad_x, pad_y = self._preprocess(image)
        outputs = self.session.run(self.output_names, {self.input_name: blob})
        predictions = self._prepare_predictions(outputs)
        if predictions.size == 0:
            return []
        return self._postprocess_predictions(
            predictions,
            image.shape[:2],
            blob.shape[2:],
            ratio,
            pad_x,
            pad_y,
            confidence,
            iou,
        )

    def _preprocess(self, image):
        source_height, source_width = image.shape[:2]
        target_height, target_width = self._input_hw()
        ratio = min(target_width / source_width, target_height / source_height)
        resized_width = int(round(source_width * ratio))
        resized_height = int(round(source_height * ratio))
        resized = cv2.resize(image, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)

        pad_width = target_width - resized_width
        pad_height = target_height - resized_height
        left = int(round(pad_width / 2 - 0.1))
        right = int(round(pad_width / 2 + 0.1))
        top = int(round(pad_height / 2 - 0.1))
        bottom = int(round(pad_height / 2 + 0.1))
        padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))

        blob = padded.transpose(2, 0, 1)[None].astype(np.float32) / 255.0
        return np.ascontiguousarray(blob), ratio, left, top

    def _input_hw(self):
        shape = self.session.get_inputs()[0].shape
        if len(shape) >= 4:
            channels = self._shape_dim(shape[1])
            if channels in {1, 3}:
                height = self._shape_dim(shape[2])
                width = self._shape_dim(shape[3])
            else:
                height = self._shape_dim(shape[1])
                width = self._shape_dim(shape[2])
            if height and width:
                return height, width
        return 640, 640

    def _shape_dim(self, value):
        if isinstance(value, int) and value > 0:
            return value
        if isinstance(value, str) and value.isdigit():
            parsed = int(value)
            if parsed > 0:
                return parsed
        return None

    def _prepare_predictions(self, outputs):
        output = None
        for item in outputs:
            array = np.asarray(item)
            if array.ndim >= 2:
                output = array
                break
        if output is None:
            return np.empty((0, 0), dtype=np.float32)

        output = np.squeeze(output)
        if output.ndim != 2:
            return np.empty((0, 0), dtype=np.float32)
        if output.shape[0] < output.shape[1] and output.shape[0] <= 512:
            output = output.T
        return output.astype(np.float32, copy=False)

    def _postprocess_predictions(self, predictions, original_shape, input_shape, ratio, pad_x, pad_y, confidence, iou):
        if predictions.shape[1] < 5:
            return []

        boxes_xywh = predictions[:, :4].copy()
        if boxes_xywh.size and np.nanmax(boxes_xywh) <= 2.0:
            boxes_xywh[:, [0, 2]] *= input_shape[1]
            boxes_xywh[:, [1, 3]] *= input_shape[0]

        scores, class_ids = self._class_scores(predictions)
        valid = np.isfinite(scores) & (scores >= float(confidence))
        if not np.any(valid):
            return []

        boxes_xywh = boxes_xywh[valid]
        scores = scores[valid]
        class_ids = class_ids[valid]
        boxes = self._scale_boxes(boxes_xywh, original_shape, ratio, pad_x, pad_y)
        valid_boxes = (boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])
        if not np.any(valid_boxes):
            return []

        boxes = boxes[valid_boxes]
        scores = scores[valid_boxes]
        class_ids = class_ids[valid_boxes]
        keep = self._nms(boxes, scores, class_ids, confidence, iou)
        return [self._format_detection(boxes[index], scores[index], class_ids[index], original_shape) for index in keep]

    def _class_scores(self, predictions):
        class_count = len(self.class_names)
        has_objectness = predictions.shape[1] == class_count + 5 if class_count else predictions.shape[1] == 85
        if has_objectness:
            class_scores = predictions[:, 5:]
            objectness = predictions[:, 4]
        else:
            class_scores = predictions[:, 4:]
            objectness = None

        if class_scores.shape[1] == 0:
            return np.zeros(predictions.shape[0], dtype=np.float32), np.zeros(predictions.shape[0], dtype=np.int32)

        class_ids = np.argmax(class_scores, axis=1).astype(np.int32)
        scores = class_scores[np.arange(class_scores.shape[0]), class_ids]
        if objectness is not None:
            scores = scores * objectness
        return scores.astype(np.float32, copy=False), class_ids

    def _scale_boxes(self, boxes_xywh, original_shape, ratio, pad_x, pad_y):
        original_height, original_width = original_shape
        cx = boxes_xywh[:, 0]
        cy = boxes_xywh[:, 1]
        width = boxes_xywh[:, 2]
        height = boxes_xywh[:, 3]

        x1 = (cx - width / 2 - pad_x) / ratio
        y1 = (cy - height / 2 - pad_y) / ratio
        x2 = (cx + width / 2 - pad_x) / ratio
        y2 = (cy + height / 2 - pad_y) / ratio

        x1 = np.clip(x1, 0, original_width)
        y1 = np.clip(y1, 0, original_height)
        x2 = np.clip(x2, 0, original_width)
        y2 = np.clip(y2, 0, original_height)
        return np.stack([x1, y1, x2, y2], axis=1)

    def _nms(self, boxes, scores, class_ids, confidence, iou):
        keep = []
        max_wh = 7680
        offset_boxes = boxes.copy()
        offsets = class_ids.astype(np.float32)[:, None] * max_wh
        offset_boxes[:, [0, 2]] += offsets
        offset_boxes[:, [1, 3]] += offsets

        order = scores.argsort()[::-1]
        while order.size > 0:
            index = int(order[0])
            keep.append(index)
            if order.size == 1:
                break
            rest = order[1:]
            overlaps = self._box_iou(offset_boxes[index], offset_boxes[rest])
            order = rest[overlaps <= float(iou)]
        return keep

    def _box_iou(self, box, boxes):
        inter_x1 = np.maximum(box[0], boxes[:, 0])
        inter_y1 = np.maximum(box[1], boxes[:, 1])
        inter_x2 = np.minimum(box[2], boxes[:, 2])
        inter_y2 = np.minimum(box[3], boxes[:, 3])
        inter_width = np.maximum(0, inter_x2 - inter_x1)
        inter_height = np.maximum(0, inter_y2 - inter_y1)
        intersection = inter_width * inter_height

        box_area = np.maximum(0, box[2] - box[0]) * np.maximum(0, box[3] - box[1])
        boxes_area = np.maximum(0, boxes[:, 2] - boxes[:, 0]) * np.maximum(0, boxes[:, 3] - boxes[:, 1])
        union = box_area + boxes_area - intersection
        return intersection / np.maximum(union, 1e-7)

    def _format_detection(self, box, score, class_id, original_shape):
        original_height, original_width = original_shape
        x = min(max(0, int(round(float(box[0])))), max(0, original_width - 1))
        y = min(max(0, int(round(float(box[1])))), max(0, original_height - 1))
        x2 = min(max(x + 1, int(round(float(box[2])))), original_width)
        y2 = min(max(y + 1, int(round(float(box[3])))), original_height)
        width = x2 - x
        height = y2 - y
        return {
            "className": self._class_name(int(class_id)),
            "confidence": round(float(score), 4),
            "bbox": {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            },
        }

    def _class_name(self, class_id):
        if 0 <= class_id < len(self.class_names):
            return self.class_names[class_id]
        return f"class_{class_id}"

    def _load_class_names(self):
        try:
            metadata = self.session.get_modelmeta()
            custom = metadata.custom_metadata_map or {}
        except Exception:
            return []
        return self._parse_class_names(custom.get("names") or custom.get("classes"))

    def _parse_class_names(self, value):
        if not value:
            return []
        if isinstance(value, str):
            parsed = None
            for parser in (json.loads, ast.literal_eval):
                try:
                    parsed = parser(value)
                    break
                except (TypeError, ValueError, SyntaxError):
                    continue
            if parsed is None:
                return [name.strip() for name in value.split(",") if name.strip()]
            value = parsed
        if isinstance(value, dict):
            return [str(name) for _, name in sorted(value.items(), key=self._class_key)]
        if isinstance(value, (list, tuple)):
            return [str(name) for name in value]
        return []

    def _class_key(self, item):
        try:
            return 0, int(item[0])
        except (TypeError, ValueError):
            return 1, str(item[0])

    def _mock_detect(self, image, confidence):
        height, width = image.shape[:2]
        if width < 32 or height < 32 or confidence > 0.95:
            return []
        box_width = max(24, int(width * 0.18))
        box_height = max(24, int(height * 0.16))
        x = max(0, int(width * 0.41))
        y = max(0, int(height * 0.38))
        return [
            {
                "className": "vehicle",
                "confidence": round(max(confidence, 0.86), 2),
                "bbox": {
                    "x": x,
                    "y": y,
                    "width": min(box_width, width - x),
                    "height": min(box_height, height - y),
                },
            }
        ]

    def _blank_image(self, width, height):
        return np.zeros((height, width, 3), dtype=np.uint8)
