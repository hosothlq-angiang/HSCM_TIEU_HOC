from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "<h1>✅ Hệ thống Quản lý Hồ sơ Chuyên môn</h1><p>Đã kết nối thành công!</p>"