from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    role = db.Column(db.String(20), default='user')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
