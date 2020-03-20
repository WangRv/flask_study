from flask import Blueprint, render_template, url_for, request, current_app
from ... import Post, Category,Comment

blog_bp = Blueprint("blog", __name__)
from .views import *
