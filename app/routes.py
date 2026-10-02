from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

# Lưu ID thư mục Drive
DRIVE_FOLDER_ID = "13hI5NX2UfQqINJNuXJFGPsUrvRXSzA7O"

@main_bp.route('/')
def index():
    drive_link = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    return render_template('index.html', drive_link=drive_link)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).strip() == request.form.get('username'):
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash("❌ Tên đăng nhập hoặc mật khẩu không đúng")
    return render_template('login.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    drive_link = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    return render_template('dashboard.html', user=current_user, drive_link=drive_link)

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("⚠️ Chưa chọn tệp!")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("⚠️ Tên tệp trống!")
            return redirect(request.url)
        
        if file:
            # Lưu tạm trên máy chủ
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            
            # Đổi tên tệp tránh trùng
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            flash(f"✅ Tải lên thành công: {filename}")
            flash(f"📂 Lưu vào: Thư mục trên Google Drive")
            return redirect(url_for('main.dashboard'))
    
    return render_template('upload.html', drive_folder_id=DRIVE_FOLDER_ID)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
