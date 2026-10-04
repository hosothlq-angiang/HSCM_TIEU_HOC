import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hscm-tieu-hoc-2026-bao-mat-cao'
    
    # ========== GMAIL GỬI THÔNG BÁO ==========
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'hoso.thlq@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = 'Hệ thống Quản lý Hồ sơ <hoso.thlq@gmail.com>'
    
    # ========== LIÊN KẾT THƯ MỤC DRIVE — ĐÃ CẬP NHẬT ĐÚNG ==========
    DRIVE_ROOT_URL = "https://drive.google.com/drive/folders/13hl5NX2UfQqINJNuXJFGPsUrvRXSzA7O"
    DRIVE_GRADE_FOLDERS = {
        "Khối 1": "https://drive.google.com/drive/folders/1QnDG18pG0c2yY5L3IK7RhKz_q54g9b2g",
        "Khối 2": "https://drive.google.com/drive/folders/1ALOCpcjL4X1LSx0q9nq7h5UmA3u7j9MW",
        "Khối 3": "https://drive.google.com/drive/folders/18A77aJ6EXmvuPhKF5322taLphygTIvds",
        "Khối 4": "https://drive.google.com/drive/folders/1VugY2AC67aLlYNNAZQj5VoQJVuvrfQ4Z",
        "Khối 5": "https://drive.google.com/drive/folders/1nRKZNEqpswJQ8-5-7uMFBHwCVa3jqCc6",
    }
