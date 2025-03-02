import cv2
import numpy as np
import os
import json

def split_table(image_path, table_coords, rows=7, cols=5):
    """
    表全体の座標を使って、セルを等分し、それぞれを正方形に正規化し、指定のフォルダに保存する。
    また、cells.json に分割されたセルの情報を保存する。

    :param image_path: 入力画像のパス
    :param table_coords: 表全体の座標（[x1, y1, x2, y2, x3, y3, x4, y4]）
    :param rows: 縦のセル数
    :param cols: 横のセル数
    :return: セルごとの画像パスリスト
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("画像を読み込めません")

    # 元画像の名前（拡張子なし）を取得し、保存ディレクトリを作成
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_dir = os.path.join("/var/www/html/opencv", base_name)
    os.makedirs(output_dir, exist_ok=True)

    # 4点の座標を変形行列でまっすぐな長方形に補正
    src_pts = np.array(table_coords, dtype=np.float32).reshape(4, 2)
    width = max(np.linalg.norm(src_pts[0] - src_pts[1]), np.linalg.norm(src_pts[2] - src_pts[3]))
    height = max(np.linalg.norm(src_pts[0] - src_pts[3]), np.linalg.norm(src_pts[1] - src_pts[2]))

    dst_pts = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    table_warped = cv2.warpPerspective(image, M, (int(width), int(height)))

    # セルのサイズ
    cell_w = int(width / cols)
    cell_h = int(height / rows)
    cell_size = max(cell_w, cell_h)  # 正方形にするための基準サイズ

    cell_paths = []
    cells_info = []  # JSONに保存するリスト

    for r in range(rows):
        for c in range(cols):
            x, y = c * cell_w, r * cell_h
            cell = table_warped[y:y + cell_h, x:x + cell_w]

            # 正方形にリサイズ
            cell_resized = cv2.resize(cell, (cell_size, cell_size))

            # `[row]_[column].jpeg` の形式で保存
            cell_filename = f"{r}_{c}.jpeg"
            cell_filepath = os.path.join(output_dir, cell_filename)
            cv2.imwrite(cell_filepath, cell_resized)
            cell_paths.append(cell_filepath)

            # JSONに記録
            cells_info.append({
                "row": r,
                "column": c,
                "filename": cell_filename
            })

    # JSONファイルに保存
    json_path = os.path.join(output_dir, "cells.json")
    with open(json_path, "w") as json_file:
        json.dump(cells_info, json_file, indent=4)

    return cell_paths

