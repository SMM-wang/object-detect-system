from collections import Counter, defaultdict

from app.models.detect_log import DetectLog
from app.utils.validators import parse_datetime


def get_summary(args, user):
    query = _scoped_query(user)
    query = _apply_time_filters(query, args)
    records = query.all()

    total_records = len(records)
    success_records = sum(1 for item in records if item.status == "success")
    failed_records = sum(1 for item in records if item.status == "failed")
    avg_elapsed_ms = round(sum(item.elapsed_ms or 0 for item in records) / total_records, 2) if total_records else 0

    return {
        "totalRecords": total_records,
        "successRecords": success_records,
        "failedRecords": failed_records,
        "avgElapsedMs": avg_elapsed_ms,
        "classDistribution": _class_distribution(records),
        "elapsedTrend": _elapsed_trend(records),
        "modelUsage": _model_usage(records),
    }


def _scoped_query(user):
    query = DetectLog.query
    if user.role != "admin":
        query = query.filter(DetectLog.user_id == user.id)
    return query


def _apply_time_filters(query, args):
    start_time = parse_datetime(args.get("startTime"), "startTime")
    end_time = parse_datetime(args.get("endTime"), "endTime")
    if start_time:
        query = query.filter(DetectLog.created_at >= start_time)
    if end_time:
        query = query.filter(DetectLog.created_at <= end_time)
    return query.order_by(DetectLog.created_at.asc())


def _class_distribution(records):
    counts = Counter()
    for record in records:
        result = record.result_json or {}
        for item in result.get("objects", []):
            counts[item.get("className", "unknown")] += 1
        for class_name, count in result.get("summary", {}).get("classes", {}).items():
            counts[class_name] += count
    return [{"className": name, "count": count} for name, count in counts.most_common()]


def _elapsed_trend(records):
    buckets = defaultdict(list)
    for record in records:
        if record.created_at:
            buckets[record.created_at.strftime("%Y-%m-%d")].append(record.elapsed_ms or 0)
    return [
        {"date": date, "avgElapsedMs": round(sum(values) / len(values), 2)}
        for date, values in sorted(buckets.items())
    ]


def _model_usage(records):
    counts = Counter(record.model_version for record in records)
    return [{"modelVersion": name, "count": count} for name, count in counts.most_common()]
