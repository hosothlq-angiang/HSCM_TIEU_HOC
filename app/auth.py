from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/dang-nhap', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Sai tên đăng nhập hoặc mật khẩu')
    return """
    <form method=post>
        <h3>Đăng nhập</h3>
        <p>Tên: <input name=username required>
        <p>Mật khẩu: <input type=password name=password required>
        <p><button type=submit>Đăng nhập</button>
    </form>
    """

@auth_bp.route('/dang-xuat')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))