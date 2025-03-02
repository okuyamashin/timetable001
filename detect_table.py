#!/usr/bin/env python3
import sys
import cv2
import numpy as np

def detect_table_bounds(image):
    """画像内の最も外側の表の枠を検出し、四隅の座標を返す"""

    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ノイズ除去（ぼかし）
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # エッジ検出（Canny）
    median = np.median(gray)
    low = int(max(0, 0.66 * median))
    high = int(min(255, 1.33 * median))

    edges = cv2.Canny(blurred, low, high)
    #edges = cv2.Canny(blurred, 50, 150)

    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    cv2.imwrite("edges_debug.png", edges)
    # 輪郭を検出（ツリー構造で取得）
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 最大の矩形を探す
    max_area = 0
    best_box = None

    for cnt in contours:
        # 面積が一定以上のものを対象とする（ノイズ除去）
        area = cv2.contourArea(cnt)
        if area < 5000:  # 小さい矩形は除外
            continue

        # 最小外接矩形（回転可能）
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = box.astype(int)  # ここを修正（np.int0 → .astype(int)）

        # アスペクト比のチェック（極端に細長いものを排除）
        width = np.linalg.norm(box[0] - box[1])
        height = np.linalg.norm(box[1] - box[2])
        aspect_ratio = max(width, height) / min(width, height)

        if aspect_ratio > 10:  # 縦長・横長すぎるものを除外
            continue

        # 最大の矩形を更新
        if area > max_area:
            max_area = area
            best_box = box

    if best_box is None:
        print("エラー: 表の枠が検出できませんでした。", file=sys.stderr)
        sys.exit(1)

    # タブ区切りで四隅の座標を出力
    return [(int(pt[0]), int(pt[1])) for pt in best_box]

def main():
    # 画像を標準入力から読み込む
    img_bytes = sys.stdin.buffer.read()
    np_arr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        print("エラー: 画像の読み込みに失敗しました。", file=sys.stderr)
        sys.exit(1)

    # 表の全体枠を検出
    corners = detect_table_bounds(image)

    # タブ区切りで出力
    print("\t".join(map(str, [coord for point in corners for coord in point])))


if __name__ == "__main__":
    main()
