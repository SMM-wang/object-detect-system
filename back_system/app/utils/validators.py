from datetime import datetime

from app.errors import ValidationError


DATETIME_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S")


def parse_float_range(name, value, min_value=0.01, max_value=1.0):
    if value is None or value == "":
        raise ValidationError(f"{name} 为必填参数")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} 必须为数字") from exc
    if parsed < min_value or parsed > max_value:
        raise ValidationError(f"{name} 必须在 {min_value} 至 {max_value} 之间")
    return parsed


def parse_int_range(name, value, min_value, max_value):
    if value is None or value == "":
        raise ValidationError(f"{name} 为必填参数")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} 必须为整数") from exc
    if parsed < min_value or parsed > max_value:
        raise ValidationError(f"{name} 必须在 {min_value} 至 {max_value} 之间")
    return parsed


def optional_int_range(name, value, default, min_value, max_value):
    if value is None or value == "":
        return default
    return parse_int_range(name, value, min_value, max_value)


def parse_positive_int(name, value, default, max_value=None):
    if value is None or value == "":
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} 必须为整数") from exc
    if parsed < 1:
        raise ValidationError(f"{name} 必须大于 0")
    if max_value and parsed > max_value:
        return max_value
    return parsed


def parse_datetime(value, name):
    if not value:
        return None
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValidationError(f"{name} 时间格式不正确")
