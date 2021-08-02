from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Post
from . import db
import json
import os

views = Blueprint('views', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
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
        # TODO !!!!!!!!!!!
        # it must still be tested whether such a file with this name 
        # already exists, or whether this title already exists.

        # check if the post request has the file part
        if 'thumbnailFile' not in request.files and 'workFile' not in request.files:
            flash('No file part!', category='error')
            return render_template('settings.html', user=current_user)
        tfile = request.files['thumbnailFile']
        wfile = request.files['workFile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if tfile.filename == '' and wfile.filename == '':
            flash('No selected file', category='error')
            return render_template('settings.html', user=current_user)
        
        # the data are stored in variables
        title = request.form.get('title')
        post_type = request.form.get('postType')
        description = request.form.get('description')
        date = request.form.get('date')

        # the files must be renamed for security purposes
        file_name = title.lower()
        file_name = file_name.replace(' ', '_')
        tfile.filename = file_name + '_preview'
        wfile.filename = file_name

        # check if all information is correct
        if len(title) < 5:
            flash('please enter a correct title!', category='error')
            return render_template('settings.html', user=current_user)
        if post_type == None:
            flash('please select a type!', category='error')
            return render_template('settings.html', user=current_user)
        if len(date) > 10:
            flash('please enter a correct date!', category='error')
            return render_template('settings.html', user=current_user)
        else:
            new_post = Post(title=title,
                            post_type = post_type,
                            file_name = file_name, 
                            description = description, 
                            date = date, 
                            user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()

            target = os.path.join(APP_ROOT, 'uploads/')
            print("Couldn't create upload directory: {}".format(target))
            destination1 = "/".join([target, tfile.filename])
            tfile.save(destination1)
            destination2 = "/".join([target, wfile.filename])
            wfile.save(destination2)

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

@views.route('/gallery')
def gallery():
    page = request.args.get('artwork', default=None, type=str)
    if page == None:
        # here comes the normal gallery
        return render_template('base.html', user=current_user)
    # under this "IF" must first be looked if this page exists
    # http://127.0.0.1:5000/gallery?artwork=test
    # after it has been checked the page can be displayed 
    # and also the view counter can be set high
    return str(page)