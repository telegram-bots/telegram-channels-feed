from flask import Blueprint

from .api_controller import APIController

bp = Blueprint("api", __name__)
bp.add_url_rule('/<img_id>', view_func=APIController.as_view("api"))
