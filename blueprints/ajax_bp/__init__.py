from flask import Blueprint

ajax_bp = Blueprint("ajax", __name__,url_prefix="/ajax")

from .ajax import *
