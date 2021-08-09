from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User
from . import db
import json
import os
import collections

views = Blueprint('views', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = set(['png'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        try:
            result = db.session.query(Post).all() # retrieves all POST elements in the database
            __dict = {}
            for post in result:
                __dict[post.date] = post
            # sort by date
            post_list = collections.OrderedDict(sorted(__dict.items(), reverse=True))
            counter = 0
            dbpost = []
            for p in post_list.items():
                if counter < 4:
                    dbpost.append(p)
                    counter = counter + 1
        except:
            dbpost = None
    return render_template('home.html', user=current_user, dbpost=dbpost)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
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

        # the file type is checked here
        if not allowed_file(tfile.filename) or not allowed_file(wfile.filename):
            if allowed_file(tfile.filename) == False:
                flash('thumbnail wrong file type', category='error')
            if allowed_file(wfile.filename) == False:
                flash('workFile wrong file type', category='error')
            return render_template('settings.html', user=current_user)

        # the data are stored in variables
        title = request.form.get('title')
        post_type = request.form.get('postType')
        description = request.form.get('description')
        user_name = current_user.first_name
        date = request.form.get('date')
        date = int(date.replace('-', ''))


        # the files must be renamed for security purposes
        file_name = title.lower()
        file_name = file_name.replace(' ', '_')
        tfile.filename = file_name + '_preview'
        wfile.filename = file_name

        # check if all information is correct
        for post in db.session.query(Post).all(): # does this entry already exist?
            if post.title == title:
                flash('There is already an entry with this title!', category='error')
                return render_template('settings.html', user=current_user)
        if len(title) < 4: # does the title have more than 4 characters?
            flash('please enter a correct title! (more than 4 characters)', category='error')
            return render_template('settings.html', user=current_user)
        if post_type == None: # one type was selected?
            flash('please select a type!', category='error')
            return render_template('settings.html', user=current_user)
        if date > 20500000: # date must be before 2050
            flash('please enter a correct date!', category='error')
            return render_template('settings.html', user=current_user)
        else:
            new_post = Post(title=title,
                            post_type = post_type,
                            file_name = file_name, 
                            description = description, 
                            date = date, 
                            user_id=current_user.id,
                            user_name = user_name,
                            views_counter = 0)
            db.session.add(new_post)
            db.session.commit()

            target = os.path.join(APP_ROOT, 'static/uploads/')
            destination1 = "/".join([target, tfile.filename + '.png'])
            tfile.save(destination1)
            destination2 = "/".join([target, wfile.filename + '.png'])
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
            # delete image files
            try:
                target = os.path.join(APP_ROOT, 'static/uploads/') + post.file_name
                os.remove(target + '.jpg')
                os.remove(target + '_preview.jpg')
            except OSError as e:
                flash(e, category='error')
                print(e)
            # delete database entry
            db.session.delete(post)
            db.session.commit()
            return jsonify({})
    return jsonify({})

@views.route('/gallery', methods=['GET'])
def gallery():
    if request.method == 'GET':
        page = request.args.get('artwork', default=None, type=str)
        if page == None:
            target = os.path.join(APP_ROOT, 'static/uploads/')
            result = db.session.query(Post).all() # retrieves all POST elements in the database
            __dict = {}
            for post in result:
                __dict[post.date] = post
            # sort by date
            post_list = collections.OrderedDict(sorted(__dict.items(), reverse=True))
            # the normal gallery is displayed here
            return render_template('gallery.html', user=current_user, post_list=post_list, target=target)
        result = db.session.query(Post).all()
        for post in result:
            if post.title == page:
                post.views_counter = post.views_counter + 1
                db.session.commit()
                return render_template('portfolio_entry.html', user=current_user, post=post)
    # if this page does not exist
    return render_template('blank_page.html', user=current_user, mes=str(page))

@views.route('/display/<filename>')
def display_image(filename):
	print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@views.route('/impressum')
def impressum():
    return render_template('impressum.html', user=current_user)