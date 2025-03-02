import cv2
import numpy as np
import os
import json


def classify_cell(cell, output_dir, r,c):
    """
    セルの画像を解析し、「空白（empty）」か「文字あり（text）」を判定
    """
    # 1. ノイズ除去（デノイズ処理）
    cell = cv2.medianBlur(cell, 3)  # メディアンフィルタでノイズ除去
    cell = cv2.fastNlMeansDenoising(cell, None, 30, 7, 21)  # 高度なノイズリダクション

    # 2. グレースケール化（念のため）
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if len(cell.shape) == 3 else cell

    # 3. 閾値処理でコントラストを強調
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # 4. モルフォロジー変換でノイズをさらに除去
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)  # 小さなノイズを除去
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel) # 文字の切れを補完

    # **追加: グレースケール画像を保存**
    gray_dir = os.path.join(output_dir, "gray")
    os.makedirs(gray_dir, exist_ok=True)
    gray_filename = f"{r}_{c}_gray.jpeg"
    gray_filepath = os.path.join(gray_dir, gray_filename)
    cv2.imwrite(gray_filepath, binary)

    # 5. 文字の密度を解析
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    total_contour_area = sum(cv2.contourArea(cnt) for cnt in contours)
    cell_area = cell.shape[0] * cell.shape[1]
    contour_ratio = total_contour_area / cell_area
    num_contours = len(contours)

    # **しきい値を更新**
    is_text = contour_ratio >= 0.9 or num_contours >= 10
    cell_type = "text" if is_text else "empty"

    return cell_type, contour_ratio, num_contours


def split_table(image_path, table_coords, rows=7, cols=5):
    """
    表全体の座標を使って、セルを等分し、それぞれを正方形に正規化し、指定のフォルダに保存する。
    また、cells.json に分割されたセルの情報を保存する。

    :param image_path: 入力画像のパス
    :param table_coords: 表全体の座標（[x1, y1, x2, y2, x3, y3, x4, x4]）
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

            # セルの種類を判定
            cell_type, contour_ratio, num_contours = classify_cell(cell_resized, output_dir, r, c) 

            gray_filename = f"{r}_{c}_gray.jpeg"

            # JSONに記録
            cells_info.append({
                "row": r,
                "column": c,
                "filename": cell_filename,
                "gray_filename": gray_filename,  # 追加: グレースケール画像名
                "type": cell_type,
                "contour_ratio": contour_ratio,  # **追加**
                "num_contours": num_contours  # **追加**
            })

    # JSONファイルに保存
    json_path = os.path.join(output_dir, "cells.json")
    with open(json_path, "w") as json_file:
        json.dump(cells_info, json_file, indent=4)

    return cell_paths

