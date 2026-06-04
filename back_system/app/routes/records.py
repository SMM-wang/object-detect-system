from flask import Blueprint, request

from app.middleware.auth import current_user, login_required
from app.services.record_service import get_record_detail, list_records
from app.utils.responses import success


records_bp = Blueprint("records", __name__)


@records_bp.get("")
@login_required
def records_route():
    return success(list_records(request.args, current_user()))


@records_bp.get("/<int:record_id>")
@login_required
def record_detail_route(record_id):
    return success(get_record_detail(record_id, current_user()))
