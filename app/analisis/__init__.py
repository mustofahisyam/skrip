from flask import Blueprint

analisis = Blueprint('analisis', __name__)

from . import views
from ..models import Permission

@analisis.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)