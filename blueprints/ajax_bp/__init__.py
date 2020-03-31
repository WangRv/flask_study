from flask import Blueprint

ajax_bp = Blueprint("ajax", __name__)

from .ajax import *
