# in routes/home.py or routes.py
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))  # or wherever your dashboard is
    return render_template('home.html')  # create a public homepage template
