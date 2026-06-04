from sqlalchemy import cast, String

from app.errors import ForbiddenError, NotFoundError
from app.models.detect_log import DetectLog
from app.utils.file_utils import format_datetime
from app.utils.pagination import paginate_query, parse_pagination
from app.utils.validators import parse_datetime


def list_records(args, user):
    page, page_size = parse_pagination(args)
    query = _scoped_query(user)
    query = _apply_filters(query, args)
    query = query.order_by(DetectLog.created_at.desc())
    total, items = paginate_query(query, page, page_size)
    return {
        "total": total,
        "page": page,
        "pageSize": page_size,
        "items": [_serialize_record_item(item) for item in items],
    }


def get_record_detail(record_id, user):
    record = DetectLog.query.get(record_id)
    if not record:
        raise NotFoundError("检测记录不存在")
    if user.role != "admin" and record.user_id != user.id:
        raise ForbiddenError()
    return _serialize_record_detail(record)


def _scoped_query(user):
    query = DetectLog.query
    if user.role != "admin":
        query = query.filter(DetectLog.user_id == user.id)
    return query


def _apply_filters(query, args):
    start_time = parse_datetime(args.get("startTime"), "startTime")
    end_time = parse_datetime(args.get("endTime"), "endTime")
    class_name = (args.get("className") or "").strip()
    model_version = (args.get("modelVersion") or "").strip()
    status = (args.get("status") or "").strip()

    if start_time:
        query = query.filter(DetectLog.created_at >= start_time)
    if end_time:
        query = query.filter(DetectLog.created_at <= end_time)
    if model_version:
        query = query.filter(DetectLog.model_version == model_version)
    if status:
        query = query.filter(DetectLog.status == status)
    if class_name:
        query = query.filter(cast(DetectLog.result_json, String).contains(class_name))
    return query


def _serialize_record_item(record):
    return {
        "id": record.id,
        "fileName": record.file_name,
        "fileType": record.file_type,
        "modelVersion": record.model_version,
        "objectCount": record.object_count,
        "elapsedMs": record.elapsed_ms,
        "status": record.status,
        "createdAt": format_datetime(record.created_at),
    }


def _serialize_record_detail(record):
    result = record.result_json or {}
    return {
        "id": record.id,
        "userId": record.user_id,
        "fileName": record.file_name,
        "fileType": record.file_type,
        "fileHash": record.file_hash,
        "modelVersion": record.model_version,
        "confidence": float(record.confidence),
        "iou": float(record.iou),
        "params": {"confidence": float(record.confidence), "iou": float(record.iou)},
        "resultJson": result,
        "result": result,
        "analysisText": record.analysis_text,
        "analysis": record.analysis_text,
        "objectCount": record.object_count,
        "elapsedMs": record.elapsed_ms,
        "status": record.status,
        "errorMsg": record.error_msg,
        "createdAt": format_datetime(record.created_at),
    }
