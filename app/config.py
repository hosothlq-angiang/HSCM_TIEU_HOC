import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hscm-tieu-hoc-2026-khoa-bao-mat'
    
    # ========== LIÊN KẾT THƯ MỤC GỐC & 5 KHỐI — ĐÃI ĐÚNG TỪ BẢNG CỦA BẠN ==========
    DRIVE_ROOT_URL = "https://drive.google.com/drive/folders/13hI5NX2UFqQlNJuXJFGPsUrvRXSzA7O"
    
    DRIVE_GRADE_FOLDERS = {
        "Khối 1": "https://drive.google.com/drive/folders/1QnDG18pG0c2yY5L3lK7RhKz_q54g9b2g",
        "Khối 2": "https://drive.google.com/drive/folders/1ALQCpcgjL4X1LSx0q9nq7h5UmA3u7j9MW",
        "Khối 3": "https://drive.google.com/drive/folders/18A77aJ6EXmvuPhKF5322taLphyqTlivds",
        "Khối 4": "https://drive.google.com/drive/folders/1VugY2AC67aLiYNAZQj5VoQJVuvrfQ4Z",
        "Khối 5": "https://drive.google.com/drive/folders/1nRKZNEqpswJQ8-5-7uMFBHwCVa3jqCc6",
    }