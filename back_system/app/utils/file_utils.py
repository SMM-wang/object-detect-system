import hashlib
from pathlib import Path

import cv2
import numpy as np
from werkzeug.utils import secure_filename

from app.errors import ValidationError


def safe_filename(filename):
    name = secure_filename(filename or "")
    if not name:
        raise ValidationError("文件名不合法")
    return name


def extension(filename):
    return Path(filename).suffix.lower().lstrip(".")


def ensure_allowed_extension(filename, allowed_extensions):
    if extension(filename) not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise ValidationError(f"文件类型不支持，仅支持 {allowed}")


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def decode_image_bytes(content):
    buffer = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValidationError("图像解码失败")
    return image


def format_datetime(value):
    if not value:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")
