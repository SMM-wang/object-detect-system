from flask import Blueprint, request

from app.middleware.auth import current_user, login_required
from app.services.statistics_service import get_summary
from app.utils.responses import success


statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.get("/summary")
@login_required
def statistics_summary_route():
    return success(get_summary(request.args, current_user()))
