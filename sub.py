from flask import Blueprint

bp = Blueprint("sub", __name__, subdomain="sub")


@bp.route("/")
def index():
    return "show sub content"