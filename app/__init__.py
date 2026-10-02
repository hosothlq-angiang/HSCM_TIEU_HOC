from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Khai báo duy nhất một lần đối tượng db
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cấu hình ứng dụng
    app.config['SECRET_KEY'] = os.environ.get(
        "SECRET_KEY", 
        "thay_khoa_bao_mat_an_toan_khi_chinh_thuc"
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///hoso.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Kết nối db với ứng dụng
    db.init_app(app)

    # Cấu hình Đăng nhập
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    # Import model sau khi db đã sẵn sàng
    from app.models import User

    with app.app_context():
        # Tạo bảng dữ liệu
        db.create_all()

        # Tạo tài khoản admin nếu chưa có
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                password_hash=generate_password_hash(
                    'Admin@123', 
                    method='pbkdf2:sha256'
                ),
                full_name='Quản trị viên Hệ thống',
                email='hoso.thlq@gmail.com',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Tạo tài khoản admin thành công")

    # Đăng ký các route
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
