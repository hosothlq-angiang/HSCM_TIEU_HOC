from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from app import db
from flask import current_app

user_permission = db.Table(
    'user_permission',
    db.Column('viewer_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('owner_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    
    staff_code = db.Column(db.String(20))
    class_room = db.Column(db.String(20))
    grade_level = db.Column(db.String(20))
    role_type = db.Column(db.String(20), default='giaovien')
    
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=False)  # ❌ Không bắt buộc

    viewable_users = db.relationship(
        'User',
        secondary=user_permission,
        primaryjoin=(user_permission.c.viewer_id == id),
        secondaryjoin=(user_permission.c.owner_id == id),
        backref='viewers',
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role_type == 'admin'

    def is_khoitruong(self):
        return self.role_type in ['khoitruong', 'KhoiTruong']

    def get_reset_token(self, expires_sec=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.id, salt='reset-password-salt')

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='reset-password-salt', max_age=3600)
        except:
            return None
        return User.query.get(user_id)

    def can_view_user(self, target_user):
        if self.is_admin():
            return True
        if self.id == target_user.id:
            return True
        if self.is_khoitruong() and self.grade_level == target_user.grade_level:
            return True
        return self.viewable_users.filter(user_permission.c.owner_id == target_user.id).first() is not None
