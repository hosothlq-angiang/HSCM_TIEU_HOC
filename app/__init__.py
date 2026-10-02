from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-key-thay-doi-sau")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///hoso.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Lưu ID thư mục Drive vào cấu hình ứng dụng
    app.config['DRIVE_FOLDER_ID'] = "13hI5NX2UfQqINJNuXJFGPsUrvRXSzA7O"
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)
    
    from app.models import User
    
    with app.app_context():
        db.create_all()
        # Tạo tài khoản admin nếu chưa có
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                password=generate_password_hash('Admin@123', method='pbkdf2:sha256'),
                full_name='Quản trị viên Hệ thống',
                email='hoso.thlq@gmail.com',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Tạo tài khoản admin thành công")
    
    # Đăng ký route
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
