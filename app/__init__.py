from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cấu hình
    app.config['SECRET_KEY'] = 'thay_bang_khoa_bao_mat_cua_ban'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hoso.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Khởi tạo CSDL
    db.init_app(app)
    
    # Quản lý đăng nhập
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # Tải mô hình & tạo bảng
    from app.models import User
    with app.app_context():
        db.create_all()
    
    # Đăng ký route
    from app.routes import main_bp
    from app.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    return app