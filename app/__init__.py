from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cấu hình ứng dụng
    app.config['SECRET_KEY'] = os.environ.get(
        "SECRET_KEY", 
        "khoa_bao_mat_an_toan_2026_hscm_tieu_hoc"
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        "DATABASE_URL", 
        "sqlite:////tmp/hoso_dulieu.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Kết nối CSDL
    db.init_app(app)

    # Cấu hình Đăng nhập
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục"
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_manager.init_app(app)

    # Tạo bảng dữ liệu & tài khoản Admin
    with app.app_context():
        # === CHÚ Ý: Dòng dưới XÓA DỮ LIỆU CŨ — chạy 1 lần rồi xóa dòng drop_all() đi ===
        db.drop_all()  # 👈 Chỉ giữ khi cần cập nhật cấu trúc, sau đó XÓA dòng này!
        # ==========================================================================
        
        db.create_all()
        
        # Tạo tài khoản Admin nếu chưa có
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='Quản trị viên Hệ thống',
                email='admin@hscm-tieu-hoc.vn',
                phone='',
                role_type='admin',
                must_change_password=False,
                is_active=True
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("✅ TẠO TÀI KHOẢN ADMIN THÀNH CÔNG")
        else:
            print("✅ Tài khoản admin đã sẵn sàng")

    # Đăng ký các tuyến đường
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
