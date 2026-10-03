from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User
from werkzeug.security import generate_password_hash

main_bp = Blueprint('main', __name__)

DRIVE_FOLDER_ID = "13hl5NX2UfQqINJNuXJFGPsUrvRXSzA7O"

# ========== TRANG CHỦ ==========
@main_bp.route('/')
def index():
    drive_link = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    return render_template('index.html', drive_link=drive_link)

# ========== ĐĂNG NHẬP ==========
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            
            # Bắt buộc đổi mật khẩu nếu lần đầu
            if user.must_change_password:
                flash("🔔 Vui lòng đổi mật khẩu để bảo mật tài khoản")
                return redirect(url_for('main.change_password'))
            
            return redirect(url_for('main.dashboard'))
        
        flash("❌ Tên đăng nhập hoặc mật khẩu không đúng")
    
    return render_template('login.html')

# ========== ĐĂNG XUẤT ==========
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# ========== TRANG TỔNG QUAN ==========
@main_bp.route('/dashboard')
@login_required
def dashboard():
    drive_link = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    return render_template('dashboard.html', user=current_user, drive_link=drive_link)

# ========== ĐỔI MẬT KHẨU ==========
@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Kiểm tra mật khẩu cũ
        if not current_user.check_password(old_password):
            flash("❌ Mật khẩu cũ không đúng")
            return redirect(url_for('main.change_password'))
        
        # Kiểm tra mật khẩu mới khớp
        if new_password != confirm_password:
            flash("❌ Mật khẩu mới không khớp")
            return redirect(url_for('main.change_password'))
        
        # Kiểm tra độ mạnh mật khẩu
        if len(new_password) < 8:
            flash("❌ Mật khẩu phải có ít nhất 8 ký tự")
            return redirect(url_for('main.change_password'))
        
        # Cập nhật mật khẩu
        current_user.set_password(new_password)
        current_user.must_change_password = False
        db.session.commit()
        
        flash("✅ Đổi mật khẩu thành công!")
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html', user=current_user)

# ========== QUẢN LÝ NGƯỜI DÙNG — CHỈ ADMIN ==========
@main_bp.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin():
        flash("❌ Bạn không có quyền truy cập trang này")
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users, user=current_user)

# ========== TẠO TÀI KHOẢN GIÁO VIÊN ==========
@main_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin():
        flash("❌ Bạn không có quyền thực hiện hành động này")
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        
        # Kiểm tra tên đăng nhập trùng
        if User.query.filter_by(username=username).first():
            flash("❌ Tên đăng nhập đã tồn tại")
            return redirect(url_for('main.create_user'))
        
        # Kiểm tra email trùng
        if User.query.filter_by(email=email).first():
            flash("❌ Email đã được sử dụng")
            return redirect(url_for('main.create_user'))
        
        # Tạo tài khoản mới
        new_user = User(
            username=username,
            full_name=full_name,
            email=email,
            phone=phone,
            role='giaovien',
            must_change_password=True  # Bắt buộc đổi mật khẩu lần đầu
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f"✅ Tạo tài khoản cho {full_name} thành công!")
        return redirect(url_for('main.manage_users'))
    
    return render_template('create_user.html')

# ========== RESET MẬT KHẨU — CHỈ ADMIN ==========
@main_bp.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin():
        flash("❌ Bạn không có quyền thực hiện hành động này")
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        user.set_password(new_password)
        user.must_change_password = True  # Bắt buộc đổi lại khi đăng nhập
        db.session.commit()
        
        flash(f"✅ Đặt lại mật khẩu cho {user.full_name} thành công!")
        return redirect(url_for('main.manage_users'))
    
    return render_template('reset_password.html', target_user=user)

# ========== QUÊN MẬT KHẨU — GỬI EMAIL ==========
@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        contact_type = request.form.get('contact_type', 'email')  # email hoặc phone
        contact_value = request.form.get('contact_value', '').strip()
        
        if contact_type == 'email':
            user = User.query.filter_by(email=contact_value).first()
            if user:
                flash(f"✅ Đã gửi hướng dẫn đặt lại mật khẩu về email: {contact_value}")
                # Lưu ý: Phần gửi email thực tế sẽ hướng dẫn bổ sung sau
            else:
                flash("❌ Email không tồn tại trong hệ thống")
        else:
            flash("🔔 Tính năng gửi qua SMS sẽ sớm được cập nhật! Vui lòng liên hệ Admin.")
    
    return render_template('forgot_password.html')
