from flask import Blueprint, Response, current_app, request

from app.middleware.auth import current_user, login_required
from app.services.detection_service import control_video_stream, detect_image, detect_video, stream_video_detection
from app.utils.responses import success


detect_bp = Blueprint("detect", __name__)


@detect_bp.get("/models")
@login_required
def list_models_route():
    return success(current_app.detector_manager.list_models())


@detect_bp.post("/image")
@login_required
def detect_image_route():
    data = detect_image(request.files.get("file"), request.form, current_user())
    return success(data)


@detect_bp.post("/video")
@login_required
def detect_video_route():
    data = detect_video(request.files.get("file"), request.form, current_user())
    return success(data)


@detect_bp.post("/video/stream")
@login_required
def stream_video_detection_route():
    stream = stream_video_detection(request.files.get("file"), request.form, current_user())
    return Response(stream, mimetype="application/x-ndjson")


@detect_bp.post("/video/stream/<stream_id>/control")
@login_required
def control_video_stream_route(stream_id):
    data = control_video_stream(stream_id, request.json.get("action"))
    return success(data)
