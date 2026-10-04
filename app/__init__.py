from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hscm_tieu_hoc.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục"
    
    mail.init_app(app)
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
        
        from app.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='Quản trị viên Hệ thống',
                email='admin@hscm-tieu-hoc.vn',
                phone='',
                role_type='admin',
                grade_level=None,
                must_change_password=False,
                is_active=True
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
    
    return app

from app import models
