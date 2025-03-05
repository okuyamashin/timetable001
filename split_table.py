import cv2
import numpy as np
import os
import json
import sys
from store_recognition import compare_to_directory, process_matching_results

def classify_cell(image, output_dir, r, c):
    height, width = image.shape[:2]
    margin_h = int(height * 0.08)
    margin_w = int(width * 0.17)
    cropped = image[margin_h:height-margin_h, margin_w:width-margin_w]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    black_pixels = np.count_nonzero(binary == 0)
    black_ratio = black_pixels / binary.size
    return "text" if black_ratio <= 0.95 else "empty", black_ratio

def split_table(image_path, table_coords,file_hash):
    rows = 7
    col_ratios_list = [
        [0.2, 0.4, 0.6, 0.8],
        [0.2, 0.4, 0.6, 0.79],
        [0.2, 0.4, 0.6, 0.78],
        [0.2, 0.4, 0.59, 0.78],
        [0.2, 0.4, 0.59, 0.78],
        [0.2, 0.39, 0.59, 0.78],
        [0.2, 0.39, 0.58, 0.77]
    ]
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("画像を読み込めません")
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_dir = os.path.join("/var/www/html/opencv", base_name)
    os.makedirs(output_dir, exist_ok=True)
    
    src_pts = np.array(table_coords, dtype=np.float32).reshape(4, 2)
    width = max(np.linalg.norm(src_pts[0] - src_pts[1]), np.linalg.norm(src_pts[2] - src_pts[3]))
    height = max(np.linalg.norm(src_pts[0] - src_pts[3]), np.linalg.norm(src_pts[1] - src_pts[2]))
    
    dst_pts = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    table_warped = cv2.warpPerspective(image, M, (int(width), int(height)))

    header_height = int(src_pts[0][1])
    header = image[:header_height, :]
    header_path = os.path.join(output_dir, "header.jpeg")
    cv2.imwrite(header_path, header)
    
    store_template_dir = "/var/www/html/opencv/store_template/"

    row_height = int(height / rows)
    cell_paths = []
    cells_info = []
    
    for r in range(rows):
        col_ratios = col_ratios_list[r]
        col_positions = [0] + [int(width * ratio) for ratio in col_ratios] + [int(width)]
        
        for c in range(len(col_positions) - 1):
            x1, x2 = col_positions[c], col_positions[c + 1]
            y1, y2 = r * row_height, (r + 1) * row_height
            cell = table_warped[y1:y2, x1:x2]
            cell_resized = cv2.resize(cell, (max(x2 - x1, row_height), max(x2 - x1, row_height)))
            
            cell_filename = f"{r}_{c}.jpeg"
            cell_filepath = os.path.join(output_dir, cell_filename)
            cv2.imwrite(cell_filepath, cell_resized)
            cell_paths.append(cell_filepath)
            
            cell_type, black_ratio = classify_cell(cell_resized, output_dir, r, c)

            store_matches = []
            if cell_type == "text":
                store_matches = compare_to_directory(cell_filepath, store_template_dir)
                store_matches = process_matching_results(store_matches)

            cells_info.append({
                "row": r,
                "column": c,
                "filename": cell_filename,
                "type": cell_type,
                "black_ratio": black_ratio,
                "store_match": store_matches
            })
    
    json_path = os.path.join(output_dir, "cells.json")
    with open(json_path, "w") as json_file:
        json.dump(
            {"cells":cells_info,"md5":file_hash}
        , json_file, indent=4)
    
    return cell_paths
