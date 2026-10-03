from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "khoa_bao_mat_an_toan_2026")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        "DATABASE_URL", 
        "sqlite:////tmp/hoso_dulieu.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_manager.init_app(app)

    with app.app_context():
        # === XÓA BẢNG CŨ — CHẠY 1 LẦN RỒI XÓA DÒNG NÀY ĐI ===
        db.drop_all()
        # ==================================================

        db.create_all()
        
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='Quản trị viên Hệ thống',
                email='admin@hscm-tieu-hoc.vn',
                role='admin',
                must_change_password=False  # Admin không cần đổi mật khẩu lần đầu
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("✅ TẠO TÀI KHOẢN ADMIN THÀNH CÔNG")
        else:
            print("✅ Tài khoản admin đã sẵn sàng")

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
