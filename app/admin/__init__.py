from flask import Blueprint

adminis = Blueprint('adminis', __name__)

from . import views
from ..models import Permission

@adminis.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)