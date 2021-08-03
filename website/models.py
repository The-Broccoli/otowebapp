from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    post_type = db.Column(db.String(20))
    file_name = db.Column(db.String(100))
    description = db.Column(db.String(10000))
    date = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_name =db.Column(db.String(200))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    post = db.relationship('Post')