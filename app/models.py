from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# Bảng phân quyền: Ai được xem thư mục của ai
user_permission = db.Table(
    'user_permission',
    db.Column('viewer_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('owner_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    full_name = db.Column(db.String(100), nullable=False)   # Cột C: HoTen
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    
    staff_code = db.Column(db.String(20))      # Cột B: MaGV
    class_room = db.Column(db.String(20))      # Cột D: Lop
    grade_level = db.Column(db.String(20))     # Cột A: Khối 1 → Khối 5
    role_type = db.Column(db.String(20), default='giaovien')  # Cột E: KhoiTruong / GiaoVien
    
    drive_folder_id = db.Column(db.String(100)) # ID thư mục cá nhân (sẽ cập nhật sau)
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=True)

    # Danh sách người mà tôi được phép xem
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
        return self.role_type == 'khoitruong' or self.role_type == 'KhoiTruong'

    def get_grade_folder_name(self):
        if self.grade_level:
            return f"KHỐI {self.grade_level.replace('Khối ', '')}"
        return None

    def can_view_user(self, target_user):
        """QUYỀN XEM CHÍNH XÁC theo yêu cầu"""
        # Admin xem tất cả
        if self.is_admin():
            return True
        # Xem chính mình
        if self.id == target_user.id:
            return True
        # Khối trưởng xem tất cả trong khối mình
        if self.is_khoitruong() and self.grade_level == target_user.grade_level:
            return True
        # Được phân quyền xem riêng
        return self.viewable_users.filter(user_permission.c.owner_id == target_user.id).first() is not None
