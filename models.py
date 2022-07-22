from enum import unique
from flask_login import UserMixin

from click import password_option
from matplotlib import image
# from pandas import nullable
from sqlalchemy import Float, ForeignKey
from .import db
# import db.sqlite as db

class Labeller(UserMixin, db.Model):
    __tablename__ = 'labeller_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(100))

class ImageInfo(db.Model):
    image_id = db.Column(db.String(200), primary_key=True)
    image_url = db.Column(db.String(300), unique=True)
    labelled = db.Column(db.Boolean, default=False)

class ResponseInfo(UserMixin, db.Model):

    dataset_entry_id = db.Column(db.Integer, primary_key=True)
    labeller_id = db.Column(db.Integer, ForeignKey("labeller_info.id"))
    image_1_id = db.Column(db.Integer, ForeignKey("image_info.image_id"))
    image_2_id = db.Column(db.Integer, ForeignKey("image_info.image_id"))
    
    image_1_score = db.Column(db.Float)
    image_2_score = db.Column(db.Float)    