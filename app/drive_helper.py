import os
import json
from flask import request, jsonify

# Lấy ID thư mục gốc từ Drive
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "13hI5NX2UfQqINJNuXJFGPsUrvRXSzA7O")

def get_drive_folder_link(folder_id):
    """Trả về link xem thư mục trên Drive"""
    return f"https://drive.google.com/drive/folders/{folder_id}"

def get_file_view_link(file_id):
    """Trả về link xem tệp"""
    return f"https://drive.google.com/file/d/{file_id}/view"