from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cấu hình
    app.config['SECRET_KEY'] = os.environ.get(
        "SECRET_KEY", 
        "thay_khoa_bao_mat_an_toan_khi_chinh_thuc"
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        "DATABASE_URL", 
        "sqlite:////tmp/hoso.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    from app.models import User

    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            try:
                admin = User(
                    username='admin',
                    password_hash=generate_password_hash('Admin@123', method='pbkdf2:sha256'),
                    full_name='Quản trị viên Hệ thống',
                    email='hoso.thlq@gmail.com',
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Tạo tài khoản admin thành công")
            except Exception as e:
                print(f"⚠️ Lỗi tạo admin: {e}")
                db.session.rollback()

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
