import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge


class ApiError(Exception):
    def __init__(self, msg, code=400, http_status=400, data=None):
        super().__init__(msg)
        self.msg = msg
        self.code = code
        self.http_status = http_status
        self.data = data


class ValidationError(ApiError):
    def __init__(self, msg, data=None):
        super().__init__(msg, 400, 400, data)


class UnauthorizedError(ApiError):
    def __init__(self, msg="未登录或 Token 失效", data=None):
        super().__init__(msg, 401, 401, data)


class ForbiddenError(ApiError):
    def __init__(self, msg="无访问权限", data=None):
        super().__init__(msg, 403, 403, data)


class NotFoundError(ApiError):
    def __init__(self, msg="资源不存在", data=None):
        super().__init__(msg, 404, 404, data)


class DetectorBusyError(ApiError):
    def __init__(self, msg="推理服务繁忙，请稍后重试", data=None):
        super().__init__(msg, 503, 503, data)


class InferenceError(ApiError):
    def __init__(self, msg="模型推理失败", data=None):
        super().__init__(msg, 500, 500, data)


def _payload(code, msg, data=None):
    return {"code": code, "msg": msg, "data": data}


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify(_payload(error.code, error.msg, error.data)), error.http_status

    @app.errorhandler(RequestEntityTooLarge)
    def handle_too_large(error):
        return jsonify(_payload(413, "上传文件过大", None)), 413

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        code = error.code or 500
        msg = error.description or "请求失败"
        return jsonify(_payload(code, msg, None)), code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logging.exception("Unhandled backend error")
        return jsonify(_payload(500, "服务内部错误", None)), 500
