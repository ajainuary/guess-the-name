from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from sqlalchemy.sql import func

from app.extensions import db
from app.extensions import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Suggestions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    edit_triplet = db.Column(db.String(256),index=True,unique=True)
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    votes = db.Column(db.Integer,default=1)

    def __repr__(self):
        return "Suggestion : %r" % self.edit_triplet
    def __init__(self,edit_triplet):
        self.edit_triplet = edit_triplet

