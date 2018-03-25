from flask import Blueprint

hasil = Blueprint('hasil', __name__)

from . import views
from ..models import Permission

@hasil.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)