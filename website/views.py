from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Post
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html', user=current_user)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        description = request.form.get('description')
        if len(description) < 1:
            flash('description is too short!', category='error')
        else:
            new_post = Post(data=description, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Seite added!', category='success')
    return render_template('settings.html', user=current_user)