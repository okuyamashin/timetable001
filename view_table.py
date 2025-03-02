from flask import Blueprint, request, render_template_string
import os
import json

view_table_bp = Blueprint('view_table', __name__)

@view_table_bp.route("/python/view_table", methods=["GET"])
def view_table():
    base_name = request.args.get("file")  # 例: "001"
    if not base_name:
        return "Error: No file specified", 400

    directory = os.path.join("/var/www/html/opencv", base_name)
    json_path = os.path.join(directory, "cells.json")

    if not os.path.exists(directory):
        return "Error: Directory not found", 404
    if not os.path.exists(json_path):
        return "Error: cells.json not found", 404

    # JSONデータを読み込む
    with open(json_path, "r") as json_file:
        cells_data = json.load(json_file)

    # 5列7行のテーブルを作成
    rows, cols = 7, 5  # 修正：7行5列に固定
    cells = [["" for _ in range(cols)] for _ in range(rows)]

    for cell in cells_data:
        r, c = cell["row"], cell["column"]
        if 0 <= r < rows and 0 <= c < cols:  # 範囲内であることを確認
            cells[r][c] = cell["filename"]

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
                /*width: 100%;*/
                text-align: center;
            }
            td {
                border: 1px solid red;
                width: 100px;
                height: 100px;
                background-size: contain;
                background-position: center;
                font-size:xx-small;
            }
        </style>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                fetch("/opencv/{{ base_name }}/cells.json")
                    .then(response => response.json())
                    .then(data => {
                        data.forEach(cell => {
                            let id = "cell_" + cell.row + "_" + cell.column;
                            let td = document.getElementById(id);
                            if (td) {
                                td.innerHTML = cell.filename;
                                td.style.backgroundImage = "url('/opencv/{{ base_name }}/" + cell.filename + "')";
                            }
                        });
                    })
                    .catch(error => console.error("Error loading JSON:", error));
            });
        </script>
    </head>
    <body>
        <h2>Table: {{ base_name }}</h2>
        <table>
            {% for r in range(rows) %}
                <tr>
                    {% for c in range(cols) %}
                        <td id="cell_{{ r }}_{{ c }}"></td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, base_name=base_name, rows=rows, cols=cols)

