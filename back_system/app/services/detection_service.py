import base64
import json
import os
import tempfile
import threading
import time
import uuid
from collections import Counter
from decimal import Decimal

import cv2
from flask import current_app

from app.errors import ValidationError
from app.extensions import db
from app.models.detect_log import DetectLog
from app.services.analysis_service import analyze_image, analyze_video
from app.utils.file_utils import decode_image_bytes, ensure_allowed_extension, safe_filename, sha256_bytes
from app.utils.validators import optional_int_range, parse_float_range


_VIDEO_STREAM_CONTROLS = {}
_VIDEO_STREAM_CONTROLS_LOCK = threading.Lock()


def detect_image(upload, form, user):
    safe_name = _validate_upload(upload, current_app.config["ALLOWED_IMAGE_EXTENSIONS"])
    model_version, confidence, iou = _parse_common_params(form)
    content = upload.read()
    if not content:
        raise ValidationError("上传文件不能为空")
    file_hash = sha256_bytes(content)
    started = time.perf_counter()
    try:
        image = decode_image_bytes(content)
        height, width = image.shape[:2]
        objects = current_app.detector_manager.detect_image(image, confidence, iou, model_version)
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        _save_record(
            user=user,
            file_name=safe_name,
            file_type="image",
            file_hash=file_hash,
            model_version=model_version,
            confidence=confidence,
            iou=iou,
            result={},
            analysis="",
            object_count=0,
            elapsed_ms=elapsed_ms,
            status="failed",
            error_msg=str(exc),
        )
        raise
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    analysis = analyze_image(objects)
    result = {
        "imageWidth": width,
        "imageHeight": height,
        "objects": objects,
    }
    record = _save_record(
        user=user,
        file_name=safe_name,
        file_type="image",
        file_hash=file_hash,
        model_version=model_version,
        confidence=confidence,
        iou=iou,
        result=result,
        analysis=analysis,
        object_count=len(objects),
        elapsed_ms=elapsed_ms,
        status="success",
    )
    return {
        "recordId": record.id,
        "imageWidth": width,
        "imageHeight": height,
        "elapsedMs": elapsed_ms,
        "objects": objects,
        "analysis": analysis,
    }


def detect_video(upload, form, user):
    safe_name = _validate_upload(upload, current_app.config["ALLOWED_VIDEO_EXTENSIONS"])
    model_version, confidence, iou = _parse_common_params(form)
    frame_interval = optional_int_range(
        "frameInterval",
        form.get("frameInterval"),
        current_app.config["DEFAULT_FRAME_INTERVAL"],
        1,
        120,
    )

    temp_path = _save_upload_to_temp(upload, safe_name)
    started = time.perf_counter()
    file_hash = _hash_file(temp_path)
    try:
        try:
            capture = cv2.VideoCapture(temp_path)
            if not capture.isOpened():
                raise ValidationError("视频解码失败")
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            max_frames = current_app.config["VIDEO_MAX_PROCESSED_FRAMES"]
            processed_frames = 0
            class_counts = Counter()
            total_objects = 0
            frame_index = 0

            while capture.isOpened() and processed_frames < max_frames:
                ok, frame = capture.read()
                if not ok:
                    break
                if frame_index % frame_interval == 0:
                    objects = current_app.detector_manager.detect_image(frame, confidence, iou, model_version)
                    processed_frames += 1
                    total_objects += len(objects)
                    class_counts.update(item["className"] for item in objects)
                frame_index += 1
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            _save_record(
                user=user,
                file_name=safe_name,
                file_type="video",
                file_hash=file_hash,
                model_version=model_version,
                confidence=confidence,
                iou=iou,
                result={},
                analysis="",
                object_count=0,
                elapsed_ms=elapsed_ms,
                status="failed",
                error_msg=str(exc),
            )
            raise
    finally:
        if "capture" in locals():
            capture.release()
        if os.path.exists(temp_path):
            os.remove(temp_path)

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    summary = {"totalObjects": total_objects, "classes": dict(class_counts)}
    analysis = analyze_video(summary)
    result = {
        "frameCount": frame_count,
        "processedFrames": processed_frames,
        "summary": summary,
    }
    record = _save_record(
        user=user,
        file_name=safe_name,
        file_type="video",
        file_hash=file_hash,
        model_version=model_version,
        confidence=confidence,
        iou=iou,
        result=result,
        analysis=analysis,
        object_count=total_objects,
        elapsed_ms=elapsed_ms,
        status="success",
    )
    return {
        "recordId": record.id,
        "elapsedMs": elapsed_ms,
        "frameCount": frame_count,
        "processedFrames": processed_frames,
        "summary": summary,
        "analysis": analysis,
    }


def stream_video_detection(upload, form, user):
    safe_name = _validate_upload(upload, current_app.config["ALLOWED_VIDEO_EXTENSIONS"])
    model_version, confidence, iou = _parse_common_params(form)
    frame_interval = optional_int_range(
        "frameInterval",
        form.get("frameInterval"),
        current_app.config["DEFAULT_FRAME_INTERVAL"],
        1,
        120,
    )

    app = current_app._get_current_object()
    temp_path = _save_upload_to_temp(upload, safe_name)
    file_hash = _hash_file(temp_path)
    stream_id = uuid.uuid4().hex
    control = {"paused": False, "stopped": False}
    with _VIDEO_STREAM_CONTROLS_LOCK:
        _VIDEO_STREAM_CONTROLS[stream_id] = control

    def generate():
        started = time.perf_counter()
        capture = None
        frame_count = 0
        processed_frames = 0
        total_objects = 0
        class_counts = Counter()
        try:
            yield json.dumps({"type": "started", "streamId": stream_id}) + "\n"
            with app.app_context():
                capture = cv2.VideoCapture(temp_path)
                if not capture.isOpened():
                    raise ValidationError("视频解码失败")
                frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                max_frames = app.config["VIDEO_MAX_PROCESSED_FRAMES"]
                frame_index = 0

                while capture.isOpened() and processed_frames < max_frames:
                    if control["stopped"]:
                        break
                    while control["paused"] and not control["stopped"]:
                        time.sleep(0.1)
                    if control["stopped"]:
                        break

                    ok, frame = capture.read()
                    if not ok:
                        break
                    if frame_index % frame_interval != 0:
                        frame_index += 1
                        continue

                    objects = app.detector_manager.detect_image(frame, confidence, iou, model_version)
                    processed_frames += 1
                    total_objects += len(objects)
                    class_counts.update(item["className"] for item in objects)

                    ok, buffer = cv2.imencode(".jpg", frame)
                    if ok:
                        yield json.dumps({
                            "type": "frame",
                            "frameIndex": frame_index,
                            "frameCount": frame_count,
                            "processedFrames": processed_frames,
                            "imageWidth": frame.shape[1],
                            "imageHeight": frame.shape[0],
                            "objects": objects,
                            "image": base64.b64encode(buffer).decode("ascii"),
                        }) + "\n"
                    frame_index += 1

                elapsed_ms = int((time.perf_counter() - started) * 1000)
                summary = {"totalObjects": total_objects, "classes": dict(class_counts)}
                analysis = analyze_video(summary)
                record = _save_record(
                    user=user,
                    file_name=safe_name,
                    file_type="video",
                    file_hash=file_hash,
                    model_version=model_version,
                    confidence=confidence,
                    iou=iou,
                    result={"frameCount": frame_count, "processedFrames": processed_frames, "summary": summary},
                    analysis=analysis,
                    object_count=total_objects,
                    elapsed_ms=elapsed_ms,
                    status="success",
                )
                yield json.dumps({
                    "type": "done",
                    "recordId": record.id,
                    "elapsedMs": elapsed_ms,
                    "frameCount": frame_count,
                    "processedFrames": processed_frames,
                    "summary": summary,
                    "analysis": analysis,
                }) + "\n"
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            with app.app_context():
                _save_record(
                    user=user,
                    file_name=safe_name,
                    file_type="video",
                    file_hash=file_hash,
                    model_version=model_version,
                    confidence=confidence,
                    iou=iou,
                    result={},
                    analysis="",
                    object_count=0,
                    elapsed_ms=elapsed_ms,
                    status="failed",
                    error_msg=str(exc),
                )
            yield json.dumps({"type": "error", "msg": str(exc)}) + "\n"
        finally:
            with _VIDEO_STREAM_CONTROLS_LOCK:
                _VIDEO_STREAM_CONTROLS.pop(stream_id, None)
            if capture is not None:
                capture.release()
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return generate()


def control_video_stream(stream_id, action):
    with _VIDEO_STREAM_CONTROLS_LOCK:
        control = _VIDEO_STREAM_CONTROLS.get(stream_id)
        if control is None:
            raise ValidationError("视频检测任务不存在或已结束")
        if action == "pause":
            control["paused"] = True
        elif action == "resume":
            control["paused"] = False
        elif action == "stop":
            control["stopped"] = True
            control["paused"] = False
        else:
            raise ValidationError("不支持的视频检测控制指令")
    return {"streamId": stream_id, "action": action}


def _validate_upload(upload, allowed_extensions):
    if upload is None:
        raise ValidationError("缺少上传文件")
    safe_name = safe_filename(upload.filename)
    ensure_allowed_extension(safe_name, allowed_extensions)
    return safe_name


def _save_upload_to_temp(upload, safe_name):
    suffix = os.path.splitext(safe_name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=current_app.config["UPLOAD_DIR"]) as temp_file:
        upload.save(temp_file)
        return temp_file.name


def _parse_common_params(form):
    model_version = (form.get("modelVersion") or "").strip()
    if not model_version:
        raise ValidationError("modelVersion 为必填参数")
    confidence = parse_float_range("confidence", form.get("confidence"))
    iou = parse_float_range("iou", form.get("iou"))
    return model_version, confidence, iou


def _save_record(user, file_name, file_type, file_hash, model_version, confidence, iou, result, analysis, object_count, elapsed_ms, status, error_msg=None):
    record = DetectLog(
        user_id=user.id,
        file_name=file_name,
        file_type=file_type,
        file_hash=file_hash,
        model_version=model_version,
        confidence=Decimal(str(confidence)),
        iou=Decimal(str(iou)),
        result_json=result,
        analysis_text=analysis,
        object_count=object_count,
        elapsed_ms=elapsed_ms,
        status=status,
        error_msg=error_msg,
    )
    db.session.add(record)
    db.session.commit()
    return record


def _hash_file(path):
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
