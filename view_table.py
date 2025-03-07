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
                float:left;
                margin-right:10px;
            }
            .header_row {
                height:50px;
                background-size: contain;
                background-position: center;
            }
            .td {
                border: 1px solid red;
                width: 200px;
                height: 200px;
                background-size: cover;
                background-position: center;
                background-repeat:no-repeat;
                font-size:xx-small;
                overflow:hidden;
            }
            .type_empty {font-size:large;font-weight:bold;color:#555;}
            .type_text {font-size:large;font-weight:bold;color:blue;}
            .type_date_only {font-size:large;font-weight:bold;color:green;}
            .num_contours {
                color:purple;
                font-weight:bold;
                font-size:large;
            }
            .contour_ratio {
                color:orange;
                font-wight:bold;
                font-size:large;
            }
            .store {
                font-weight:bold;
                color:red;
                font-size:large;
            }
            .store_score {
                font-weight:bold;
                color:red;
                font-size:large;
            }
        </style>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                fetch("../opencv/{{ base_name }}/cells.json")
                    .then(response => response.json())
                    .then(data => {
                        data.cells.forEach(cell => {
                            let id = "cell_" + cell.row + "_" + cell.column;
                            let td = document.getElementById(id);
                            if (td) {
                                td.innerHTML = cell.filename + '<br/><span class="type_'+cell.type+'">' + cell.type + "</span>"
                                ;
                                td.style.backgroundImage = "url('../opencv/{{ base_name }}/" + cell.filename + "')";

                                if(cell.store_match.length > 0) {
                                    let sm = cell.store_match[0];
                                    td.innerHTML += '<br/><span class="store">' + sm[0] + '</span>' + '<br/><span class="store_score">' + sm[1].toFixed(2) + '</span>';
                                }
                            }
                        });
                        let htd = document.getElementById('header_row');
                        htd.style.backgroundImage = "url('../opencv/{{base_name}}/header.jpeg')"; 
                    })
                    .catch(error => console.error("Error loading JSON:", error));
            });
        </script>
    </head>
    <body>
        <h2>Table: {{ base_name }}</h2>
        <table>
            <tr>
                <td colspan="5" id="header_row" class="header_row">
                </td>
            </tr>
            {% for r in range(rows) %}
                <tr>
                    {% for c in range(cols) %}
                        <td class="td" id="cell_{{ r }}_{{ c }}"></td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, base_name=base_name, rows=rows, cols=cols)

