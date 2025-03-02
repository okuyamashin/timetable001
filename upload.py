import os
import hashlib
from flask import Flask, request, render_template_string
from files import files_bp  # ← ここで files.py をインポート
from detect_table import detect_table
from draw_rectangle import draw_rectangle
from split_table import split_table

app = Flask(__name__)

UPLOAD_FOLDER = "/var/www/html/opencv"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "avi", "mov", "txt", "pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/python/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400
        if file and allowed_file(file.filename):
            file_data = file.read()
            file_hash = hashlib.md5(file_data).hexdigest()
            file_ext = os.path.splitext(file.filename)[1].lower()
            new_filename = f"{file_hash}{file_ext}"
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
        # 表の外枠を取得
        table_coords = detect_table(filepath)

        # セル分割
        cell_paths = split_table(filepath, table_coords)

        # 保存されたファイルのパスを返す
        base_name = os.path.splitext(file.filename)[0]
        return {
            "directory": f"/opencv/{base_name}/",
            "cells": [f"/opencv/{base_name}/{os.path.basename(cell)}" for cell in cell_paths]
        }
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/python/view_table", methods=["GET"])
def view_table():
    base_name = request.args.get("file")  # 例: "001"
    if not base_name:
        return "Error: No file specified", 400

    directory = os.path.join("/var/www/html/opencv", base_name)
    if not os.path.exists(directory):
        return "Error: Directory not found", 404

    # セル画像を取得
    files = sorted(os.listdir(directory))
    cells = []
    rows, cols = 6, 7  # 既定の行数と列数（必要に応じて変更）

    for r in range(rows):
        row_cells = []
        for c in range(cols):
            filename = f"{r}_{c}.jpeg"
            if filename in files:
                row_cells.append(f"/opencv/{base_name}/{filename}")
            else:
                row_cells.append("")
        cells.append(row_cells)

    # HTML をレンダリング
    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Table View</title>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
                text-align: center;
            }
            td {
                border: 1px solid black;
                width: 100px;
                height: 100px;
                background-size: cover;
                background-position: center;
            }
        </style>
    </head>
    <body>
        <h2>Table: {{ base_name }}</h2>
        <table>
            {% for row in cells %}
                <tr>
                    {% for cell in row %}
                        <td style="background-image: url('{{ cell }}');"></td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, base_name=base_name, cells=cells)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

