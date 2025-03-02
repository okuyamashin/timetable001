import os
from flask import Blueprint, render_template_string

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = "/var/www/html/opencv"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

@files_bp.route("/python/files")
def list_files():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        files = [f for f in files if f.split('.')[-1].lower() in ALLOWED_EXTENSIONS]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True)
    except Exception as e:
        return f"Error reading directory: {str(e)}"

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Image List</title>
        <style>
            .img_div {
                margin: 10px;
                float: left;
            }
            .img {
                width: 200px;
            }
            .img_name {
                margin: 0;
            }
            .clear {
                clear: both;
            }
        </style>
    </head>
    <body>
        <a href="/python/">Upload</a>
        <div class="list">
        {% for file in files %}
            <div class="img_div">
                <p class="img_name">{{ file }}</p>
 
                <a href="/python/view_table?file={{ file.split('.')[0] }}">
                    <img class="img" src="/opencv/{{ file }}" alt="{{ file }}">
                </a>
            </div>
        {% endfor %}
        <div class="clear"></div>
        </div>
    </body>
    </html>
    """, files=files)

