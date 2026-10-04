from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import db, mail
from app.models import User
from app.config import Config
import re

main_bp = Blueprint('main', __name__)
config = Config()

# ========== KIỂM TRA MẬT KHẨU ==========
def check_password_rule(password):
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"
    if not re.search(r'[@#]', password):
        return False, "Mật khẩu phải chứa ký tự @ hoặc #"
    return True, "OK"

# ========== TRANG CHÍNH / BẢNG ĐIỀU KHIỂN ==========
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Thông báo gợi ý đổi mật khẩu — KHÔNG BẮT BUỘC
    if current_user.must_change_password:
        flash("💡 Gợi ý: Đổi mật khẩu để bảo mật hơn → Tài khoản vẫn hoạt động bình thường", "info")
    
    # Link thư mục theo quyền
    grade_folder_url = None
    if current_user.is_admin():
        # Admin thấy thư mục gốc toàn trường
        root_url = config.DRIVE_ROOT_URL
    else:
        root_url = None
        # Giáo viên/Khối trưởng thấy thư mục khối
        if current_user.grade_level and current_user.grade_level in config.DRIVE_GRADE_FOLDERS:
            grade_folder_url = config.DRIVE_GRADE_FOLDERS[current_user.grade_level]
    
    # Danh sách người dùng có quyền xem
    viewable_list = []
    if current_user.is_admin():
        all_users = User.query.order_by(User.grade_level.asc(), User.full_name.asc()).all()
        viewable_list = [u for u in all_users if u.id != current_user.id]
    elif current_user.grade_level:
        same_grade = User.query.filter_by(grade_level=current_user.grade_level).order_by(User.full_name.asc()).all()
        if current_user.is_khoitruong():
            viewable_list = [u for u in same_grade if u.id != current_user.id]
        else:
            viewable_list = [u for u in same_grade if u.id != current_user.id and current_user.can_view_user(u)]
    
    return render_template('dashboard.html', 
                           user=current_user,
                           config=config,
                           root_url=root_url,
                           grade_folder_url=grade_folder_url,
                           viewable_list=viewable_list)

# ========== ĐĂNG NHẬP / ĐĂNG XUẤT ==========
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
            # Chỉ gợi ý, KHÔNG chuyển hướng bắt buộc
            if user.must_change_password:
                flash("💡 Gợi ý: Đổi mật khẩu để bảo mật hơn", "info")
            return redirect(url_for('main.dashboard'))
        
        flash("Tên đăng nhập hoặc mật khẩu không đúng", "error")
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Đăng xuất thành công", "info")
    return redirect(url_for('main.login'))

# ========== ĐỔI MẬT KHẨU — ĐÃ SỬA HOẠT ĐỘNG ==========
@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pass = request.form.get('old_password', '')
        new_pass = request.form.get('new_password', '')
        confirm_pass = request.form.get('confirm_password', '')
        
        # Kiểm tra mật khẩu cũ đúng
        if not current_user.check_password(old_pass):
            flash("❌ Mật khẩu cũ không đúng", "error")
            return redirect(url_for('main.change_password'))
        
        # Kiểm tra khớp mật khẩu mới
        if new_pass != confirm_pass:
            flash("❌ Mật khẩu xác nhận không khớp", "error")
            return redirect(url_for('main.change_password'))
        
        # Kiểm tra quy tắc có @ hoặc #
        valid, msg = check_password_rule(new_pass)
        if not valid:
            flash(f"❌ {msg}", "error")
            return redirect(url_for('main.change_password'))
        
        # Lưu mật khẩu mới
        current_user.set_password(new_pass)
        current_user.must_change_password = False
        db.session.commit()
        
        flash("✅ Đổi mật khẩu thành công!", "success")
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html')

# ========== QUÊN MẬT KHẨU ==========
@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        contact = request.form.get('contact', '').strip()
        method = request.form.get('method', 'email')
        
        user = None
        if '@' in contact:
            user = User.query.filter_by(email=contact).first()
        else:
            user = User.query.filter_by(phone=contact).first()
        
        if user:
            token = user.get_reset_token()
            reset_url = url_for('main.reset_password_token', token=token, _external=True)
            
            if method == 'email' and user.email:
                try:
                    msg = Message('Đặt lại mật khẩu — Hệ thống Quản lý Hồ sơ', recipients=[user.email])
                    msg.body = f"""Xin chào {user.full_name},

Bạn yêu cầu đặt lại mật khẩu tài khoản. Nhấn liên kết dưới đây để đặt mật khẩu mới:

{reset_url}

Liên kết có hiệu lực trong 1 giờ. Nếu không phải bạn, vui lòng bỏ qua.

Trân trọng,
Quản trị viên
"""
                    mail.send(msg)
                    flash(f"✅ Đã gửi hướng dẫn đến: {user.email}", "success")
                except Exception as e:
                    flash("⚠️ Không thể gửi mail. Liên hệ Admin đặt lại trực tiếp", "warning")
            elif method == 'phone' and user.phone:
                flash(f"✅ Yêu cầu đã nhận! Liên hệ Admin cấp mật khẩu mới qua: {user.phone}", "success")
            else:
                flash("Thông tin không khớp với phương thức chọn", "error")
        else:
            flash("Nếu thông tin khớp, chúng tôi sẽ gửi hướng dẫn đặt lại mật khẩu", "info")
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html')

@main_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash("Liên kết không hợp lệ hoặc đã hết hạn", "error")
        return redirect(url_for('main.forgot_password'))
    
    if request.method == 'POST':
        new_pass = request.form.get('new_password', '')
        confirm_pass = request.form.get('confirm_password', '')
        
        if new_pass != confirm_pass:
            flash("❌ Mật khẩu không khớp", "error")
            return redirect(url_for('main.reset_password_token', token=token))
        
        valid, msg = check_password_rule(new_pass)
        if not valid:
            flash(f"❌ {msg}", "error")
            return redirect(url_for('main.reset_password_token', token=token))
        
        user.set_password(new_pass)
        user.must_change_password = False
        db.session.commit()
        flash("✅ Đặt lại mật khẩu thành công! Đăng nhập với mật khẩu mới", "success")
        return redirect(url_for('main.login'))
    
    return render_template('reset_password_form.html', token=token)

# ========== QUẢN LÝ TÀI KHOẢN ==========
@main_bp.route('/manage-users')
@login_required
def manage_users():
    if not current_user.is_admin():
        flash("Bạn không có quyền truy cập", "error")
        return redirect(url_for('main.dashboard'))
    
    users = User.query.order_by(
        User.grade_level.asc(),
        User.role_type.desc(),
        User.full_name.asc()
    ).all()
    
    return render_template('manage_users.html', users=users)

@main_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin():
        flash("Bạn không có quyền truy cập", "error")
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        staff_code = request.form.get('staff_code', '').strip()
        class_room = request.form.get('class_room', '').strip()
        grade_level = request.form.get('grade_level', '').strip()
        role_type = request.form.get('role_type', 'giaovien').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None
        password = request.form.get('password', 'Giaovien@123').strip()
        
        if User.query.filter_by(username=username).first():
            flash("❌ Tên đăng nhập đã tồn tại! Chọn tên khác", "error")
            return redirect(url_for('main.create_user'))
        if User.query.filter_by(email=email).first():
            flash("❌ Email đã được sử dụng", "error")
            return redirect(url_for('main.create_user'))
        
        valid, msg = check_password_rule(password)
        if not valid:
            flash(f"❌ {msg}", "error")
            return redirect(url_for('main.create_user'))
        
        new_user = User(
            username=username,
            full_name=full_name,
            staff_code=staff_code,
            class_room=class_room,
            grade_level=grade_level,
            role_type=role_type,
            email=email,
            phone=phone,
            must_change_password=False  # Không bắt buộc đổi
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"✅ Tạo tài khoản {full_name} thành công! Tên: {username} | MK: {password}", "success")
        return redirect(url_for('main.manage_users'))
    
    return render_template('create_user.html')
