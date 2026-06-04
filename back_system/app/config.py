import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def _bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _sqlite_url(value):
    if value.startswith("sqlite:///"):
        db_path = value.replace("sqlite:///", "", 1)
        if not Path(db_path).is_absolute():
            return f"sqlite:///{(BASE_DIR / db_path).as_posix()}"
    return value


def _path_env(name, default):
    value = os.getenv(name, default)
    path = Path(value)
    if not path.is_absolute():
        path = BASE_DIR / path
    return str(path)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_EXPIRES_SECONDS = int(os.getenv("JWT_EXPIRES_SECONDS", "86400"))
    USE_MYSQL = _bool_env("USE_MYSQL", False)
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("MYSQL_DATABASE_URL")
        if USE_MYSQL
        else _sqlite_url(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    UPLOAD_MAX_BYTES = int(os.getenv("UPLOAD_MAX_BYTES", str(500 * 1024 * 1024)))
    MAX_CONTENT_LENGTH = UPLOAD_MAX_BYTES
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4"}
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))

    MODEL_BACKEND = os.getenv("MODEL_BACKEND", "onnx")
    MODEL_DIR = _path_env("MODEL_DIR", str(BASE_DIR / "model"))
    MODEL_PATH = _path_env("MODEL_PATH", str(BASE_DIR / "yolov11n.onnx"))
    MODEL_VERSION = os.getenv("MODEL_VERSION", "yolov11n.onnx")
    ALLOW_MOCK_DETECTOR = _bool_env("ALLOW_MOCK_DETECTOR", False)
    DETECTOR_MAX_CONCURRENCY = int(os.getenv("DETECTOR_MAX_CONCURRENCY", "1"))
    DETECTOR_ACQUIRE_TIMEOUT_SECONDS = float(os.getenv("DETECTOR_ACQUIRE_TIMEOUT_SECONDS", "0.1"))

    VIDEO_MAX_PROCESSED_FRAMES = int(os.getenv("VIDEO_MAX_PROCESSED_FRAMES", "300"))
    DEFAULT_FRAME_INTERVAL = int(os.getenv("DEFAULT_FRAME_INTERVAL", "5"))
