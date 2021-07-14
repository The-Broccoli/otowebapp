from flask import Blueprint, render_template
from flask_login import login_required, current_user


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)