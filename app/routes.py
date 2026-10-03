from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from app import db
from app.models import User

main_bp = Blueprint('main', __name__)

DRIVE_FOLDER_ID = "13hI5NX2UfQqINJNuXJFGPsUrvRXSzA7O"

@main_bp.route('/')
def index():
    drive_link = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    return render_template('index.html', drive_link=drive_link)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        
        flash("❌ Tên đăng nhập hoặc mật khẩu không đúng")
    
    return render_template('login.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    drive_link = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    return render_template('dashboard.html', user=__user__, drive_link=drive_link)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
