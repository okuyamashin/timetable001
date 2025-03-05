import os
import hashlib
import base64
from flask import Flask, request, render_template_string
from files import files_bp  # ← ここで files.py をインポート
from detect_table import detect_table
from draw_rectangle import draw_rectangle
from split_table import split_table
from view_table import view_table_bp

app = Flask(__name__)

UPLOAD_FOLDER = "/var/www/html/opencv"
ALLOWED_EXTENSIONS = {"jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/python/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return "No selected file", 400
            if file and allowed_file(file.filename):
                file_data = file.read()
            else:
               return "jpeg only", 400 
        elif "image_base64" in request.json:
            try:
                file_data = base64.b64decode(request.json["image_base64"])
            except Exception as e:
                return f"Invalid base64 data: {str(e)}", 400
        else:
            return "No file part", 400
        
        file_hash = hashlib.md5(file_data).hexdigest()
        new_filename = f"{file_hash}.jpeg"
        filepath = os.path.join(UPLOAD_FOLDER, new_filename)

        with open(filepath, "wb") as f:
            f.write(file_data)

        return render_template_string("""
        <html>
        <head><meta charset="UTF-8"><title>Upload Success</title></head>
        <body>
            <h2>File uploaded successfully!</h2>
            <p>Original File: {{ filename }}</p>
            <p>Saved File: {{ new_filename }}</p>
            <a href="/opencv/{{ new_filename }}" target="_blank">View File</a>
        </body>
        </html>
        """, filename=file.filename, new_filename=new_filename)

    return '''
    <!doctype html>
    <title>Upload File</title>
    <h1>Upload a file</h1>
    <form action="/python/" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    '''

# files.py のルートを Flask アプリに登録
app.register_blueprint(files_bp)

@app.route("/python/detect_table", methods=["POST"])
def detect_table_api():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in {".png", ".jpg", ".jpeg"}:
        return {"error": "Invalid file type"}, 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        coords = detect_table(filepath)
        return {"coordinates": coords}
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/python/draw_rectangle", methods=["POST"])
def draw_rectangle_api():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in {".png", ".jpg", ".jpeg"}:
        return {"error": "Invalid file type"}, 400

    # 画像を保存
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # 矩形を検出
        coords = detect_table(filepath)

        # 赤い矩形を描画
        output_filepath = os.path.join(UPLOAD_FOLDER, f"rect_{file.filename}")
        draw_rectangle(filepath, output_filepath, coords)

        return {
            "original_image": f"/opencv/{file.filename}",
            "rect_image": f"/opencv/rect_{file.filename}",
            "coordinates": coords
        }
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/python/split_table", methods=["POST"])
def split_table_api():
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400
        if file and allowed_file(file.filename):
            file_data = file.read()
        else:
            return "jpeg only", 400 
    elif "image_base64" in request.json:
        try:
            file_data = base64.b64decode(request.json["image_base64"])
        except Exception as e:
            return f"Invalid base64 data: {str(e)}", 400
    else:
            return "No file part", 400
        
    file_hash = hashlib.md5(file_data).hexdigest()
    filename = f"{file_hash}.jpeg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(file_data)

    """
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in {".png", ".jpg", ".jpeg"}:
        return {"error": "Invalid file type"}, 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    """

    try:
        # 表の外枠を取得
        table_coords = detect_table(filepath)

        # セル分割       
        cell_paths = split_table(filepath, table_coords, file_hash)

        # 保存されたファイルのパスを返す
        base_name = os.path.splitext(filename)[0]
        return {
            "directory": f"/opencv/{base_name}/",
            "md5": f"{file_hash}",
            "cells": [f"/opencv/{base_name}/{os.path.basename(cell)}" for cell in cell_paths]
        }
    except Exception as e:
        return {"error": str(e)}, 400

#表示
app.register_blueprint(view_table_bp)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

