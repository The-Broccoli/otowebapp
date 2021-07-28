from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Post
from . import db
import json
import os

views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        result = db.session.query(Post).all() # retrieves all POST elements in the database
        result.reverse() # rotates the list so that the last entries are at the front
        result = result[0:4] # we save only the first 4 results in the list
    return render_template('home.html', user=current_user, dbpost=result)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'thumbnailFile' not in request.files and 'workFile' not in request.files:
            flash('No file part!', category='error')
        tfile = request.files['thumbnailFile']
        wfile = request.files['workFile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if tfile.filename == '' and wfile.filename == '':
            flash('No selected file', category='error')
        

        title = request.form.get('title')
        post_type = request.form.get('postType')
        description = request.form.get('description')
        date = request.form.get('date')

        if len(description) < 1:
            flash('description is too short!', category='error')
        if post_type == None:
            flash('please select a type!', category='error')
        else:
            new_post = Post(title=title,
                            post_type = post_type,
                            file_name = 'TEST_FILENAME', 
                            description = description, 
                            date = date, 
                            user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Seite added!', category='success')
    return render_template('settings.html', user=current_user)

@views.route('/delete-post', methods=['POST'])
def delete_post():
    post = json.loads(request.data)
    postId = post['postId']
    post = Post.query.get(postId)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()
            return jsonify({})
    return jsonify({})