import os
import hashlib
from flask import Flask, request, render_template_string

app = Flask(__name__)

UPLOAD_FOLDER = "/var/www/html/opencv"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "avi", "mov", "txt", "pdf"}

# 必要ならディレクトリを作成
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

