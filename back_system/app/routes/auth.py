from flask import Blueprint, request

from app.services.auth_service import login
from app.utils.responses import success


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login_route():
    return success(login(request.get_json(silent=True) or {}))
