from flask import jsonify


def success(data=None, msg="success", code=200, http_status=200):
    return jsonify({"code": code, "msg": msg, "data": data if data is not None else {}}), http_status


def fail(msg, code=400, http_status=400, data=None):
    return jsonify({"code": code, "msg": msg, "data": data}), http_status
