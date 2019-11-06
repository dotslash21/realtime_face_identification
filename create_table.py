import sys
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

BASE_PATH = sys.path[0]
SQLALCHEMY_DATABASE_URI = "sqlite:///" + \
    BASE_PATH + "/faserver/database/users.db"
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<USER-{0}>".format(self.id)


class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String(40), nullable=False)
    camera_serial_num = db.Column(db.String(20), nullable=False)
    camera_token = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return "<CAMERA-{0}-{1}-{2}>".format(self.id,
                                             self.camera_name,
                                             self.camera_serial_num)

db.create_all()
db.session.commit()