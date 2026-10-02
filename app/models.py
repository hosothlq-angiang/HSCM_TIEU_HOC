from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user') # admin / user
    profile = db.relationship('Profile', backref='user', uselist=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_of_birth = db.Column(db.String(20))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    degree = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    work_unit = db.Column(db.String(200))
    experience_years = db.Column(db.Integer, default=0)
    certificates = db.Column(db.Text)
    research_works = db.Column(db.Text)
    drive_folder_id = db.Column(db.String(200)) # Lưu thư mục trên Google Drive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)