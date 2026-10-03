from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.config import Config
from werkzeug.security import generate_password_hash, check_password_hash

main_bp = Blueprint('main', __name__)
config = Config()

# ========== TRANG CHÍNH / BẢNG ĐIỀU KHIỂN ==========
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Lấy link thư mục khối — khớp chính xác định dạng "Khối 1"
    grade_folder_url = None
    if current_user.grade_level:
        grade_folder_url = config.DRIVE_GRADE_FOLDERS.get(current_user.grade_level)
    
    # Lấy danh sách người có quyền xem
    viewable_list = []
    
    if current_user.is_admin():
        # Admin xem tất cả
        all_users = User.query.order_by(User.grade_level, User.full_name).all()
        viewable_list = [u for u in all_users if u.id != current_user.id]
    elif current_user.grade_level:
        # Lấy tất cả cùng khối
        same_grade = User.query.filter_by(grade_level=current_user.grade_level).order_by(User.full_name).all()
        
        if current_user.is_khoitruong():
            # Khối trưởng xem tất cả trong khối
            viewable_list = [u for u in same_grade if u.id != current_user.id]
        else:
            # Giáo viên thường: chỉ xem người được phân quyền
            for u in same_grade:
                if u.id != current_user.id and current_user.can_view_user(u):
                    viewable_list.append(u)
    
    return render_template('dashboard.html',
                         user=current_user,
                         config=config,
                         grade_folder_url=grade_folder_url,
                         viewable_list=viewable_list)

# ========== ĐĂNG NHẬP / ĐĂNG XUẤT ==========
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            
            if user.must_change_password:
                flash("Vui lòng đổi mật khẩu để bảo mật tài khoản", "info")
                return redirect(url_for('main.change_password'))
            
            return redirect(url_for('main.dashboard'))
        
        flash("Tên đăng nhập hoặc mật khẩu không đúng", "error")
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất thành công", "info")
    return redirect(url_for('main.login'))

# ========== ĐỔI MẬT KHẨU ==========
@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(old_password):
            flash("Mật khẩu cũ không đúng", "error")
            return redirect(url_for('main.change_password'))
        
        if new_password != confirm_password:
            flash("Mật khẩu mới không khớp", "error")
            return redirect(url_for('main.change_password'))
        
        if len(new_password) < 6:
            flash("Mật khẩu mới phải có ít nhất 6 ký tự", "error")
            return redirect(url_for('main.change_password'))
        
        current_user.set_password(new_password)
        current_user.must_change_password = False
        db.session.commit()
        
        flash("✅ Đổi mật khẩu thành công!", "success")
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html', user=current_user)

# ========== QUẢN LÝ TÀI KHOẢN ==========
@main_bp.route('/manage-users')
@login_required
def manage_users():
    if not current_user.is_admin():
        flash("Bạn không có quyền truy cập trang này", "error")
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
        flash("Bạn không có quyền truy cập trang này", "error")
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        staff_code = request.form.get('staff_code', '').strip()
        class_room = request.form.get('class_room', '').strip()
        grade_level = request.form.get('grade_level', '').strip()
        role_type = request.form.get('role_type', 'giaovien').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', 'GiaoVien@123').strip()

        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại!", "error")
            return redirect(url_for('main.create_user'))
        
        if User.query.filter_by(email=email).first():
            flash("Email đã được sử dụng!", "error")
            return redirect(url_for('main.create_user'))

        new_user = User(
            username=username,
            full_name=full_name,
            staff_code=staff_code,
            class_room=class_room,
            grade_level=grade_level,
            role_type=role_type,
            email=email,
            phone=phone if phone else None,
            must_change_password=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f"✅ Tạo tài khoản {full_name} thành công!", "success")
        return redirect(url_for('main.manage_users'))
    
    return render_template('create_user.html')

@main_bp.route('/reset-password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin():
        flash("Bạn không có quyền thực hiện hành động này", "error")
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if user.is_admin():
        flash("Không thể đặt lại mật khẩu tài khoản quản trị", "error")
        return redirect(url_for('main.manage_users'))
    
    if request.method == 'POST':
        new_pass = request.form.get('new_password', 'GiaoVien@123')
        user.set_password(new_pass)
        user.must_change_password = True
        db.session.commit()
        flash(f"✅ Đặt lại mật khẩu cho {user.full_name} thành công!", "success")
        return redirect(url_for('main.manage_users'))
    
    return render_template('reset_password.html', user=user)


# ========== QUÊN MẬT KHẨU — GỬI EMAIL ==========
@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.email == email and user.is_active:
            # Tạo mật khẩu tạm hoặc yêu cầu Admin đặt lại
            flash("✅ Thông tin hợp lệ! Vui lòng liên hệ Quản trị viên để đặt lại mật khẩu", "success")
            flash("📞 Điện thoại/Zalo: [Số điện thoại Admin của bạn]", "info")
            return redirect(url_for('main.login'))
        else:
            flash("❌ Tên đăng nhập hoặc Email không khớp với hệ thống", "error")
    
    return render_template('forgot_password.html')
