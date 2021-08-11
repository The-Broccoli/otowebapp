from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User
from . import db
import json
import os
from datetime import datetime

views = Blueprint('views', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = set(['png'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def all_post(cUser = None):
    # this function takes all database entries from POST and sorts them by date 
    if cUser == None:
        result = db.session.query(Post).all() # retrieves all POST elements in the database
    if cUser:
        result = cUser.post
    sort_list = []
    # he sort_list is filled with the database content
    # sort_list [[STR 2021-01-01, CLASS post],
    #            [STR 2021-01-01, CLASS post]]
    for post in result:
        time = str(post.date)
        test = str(time[:4]) + '-' + str(time[4:6]) + '-' + str(time[6:8])
        sort_list.append([test,post])
    # sort by date
    sort_list.sort(key=lambda tup: datetime.strptime(tup[0], "%Y-%m-%d"))
    # The outer list is now removed, that only the POST classes are in a list
    post_list = []
    for p in sort_list:
        post_list.append(p[1])
    post_list.reverse()
    del sort_list
    return post_list


@views.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        try:
            post_list = all_post()
            post_list = post_list[:4]
        except:
            post_list = None
    return render_template('home.html', user=current_user, post_list=post_list)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    try:
        post_list = all_post(current_user)
    except:
        post_list = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'thumbnailFile' not in request.files and 'workFile' not in request.files:
            flash('No file part!', category='error')
            return render_template('settings.html', user=current_user, post_list=post_list)
        tfile = request.files['thumbnailFile']
        wfile = request.files['workFile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if tfile.filename == '' and wfile.filename == '':
            flash('No selected file', category='error')
            return render_template('settings.html', user=current_user, post_list=post_list)

        # the file type is checked here
        if not allowed_file(tfile.filename) or not allowed_file(wfile.filename):
            if allowed_file(tfile.filename) == False:
                flash('thumbnail wrong file type', category='error')
            if allowed_file(wfile.filename) == False:
                flash('workFile wrong file type', category='error')
            return render_template('settings.html', user=current_user, post_list=post_list)

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
                return render_template('settings.html', user=current_user, post_list=post_list)
        if len(title) < 4: # does the title have more than 4 characters?
            flash('please enter a correct title! (more than 4 characters)', category='error')
            return render_template('settings.html', user=current_user, post_list=post_list)
        if post_type == None: # one type was selected?
            flash('please select a type!', category='error')
            return render_template('settings.html', user=current_user, post_list=post_list)
        if date > 20500000: # date must be before 2050
            flash('please enter a correct date!', category='error')
            return render_template('settings.html', user=current_user, post_list=post_list)
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
    return render_template('settings.html', user=current_user, post_list=post_list)

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
                os.remove(target + '.png')
                os.remove(target + '_preview.png')
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
        pageId = request.args.get('page', default=None, type=int)
        if pageId:
            # Calculate which POST will be displayed
            # page 1 = 1-8
            # page 2 = 9-16
            # page 3 = 17-24
            # ....
            endRange = 8 * pageId
            startRange = (8 * pageId) - 8
            try:
                post_list = all_post()
                # if there is a rest must be calculated a page exrta displays
                if len(post_list) % 8:
                    page_list = int(len(post_list) / 8) + 1
                # otherwise you can divide it exactly by 8
                else:
                    page_list = int(len(post_list) / 8)
                post_list = post_list[startRange:endRange]
            except:
                post_list = None
            del endRange, startRange
            return render_template('gallery.html', user=current_user, 
                                                post_list=post_list, 
                                                page_list=page_list, 
                                                current_page_id= pageId)
        if page == None:
            try:
                post_list = all_post()
            except:
                post_list = None
            # the normal gallery is displayed here
            return render_template('gallery.html', user=current_user, post_list=post_list)
        if page:
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