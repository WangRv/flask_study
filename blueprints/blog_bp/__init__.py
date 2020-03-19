from flask import Blueprint, render_template, url_for

blog_bp = Blueprint("blog", __name__)
from .views import *
