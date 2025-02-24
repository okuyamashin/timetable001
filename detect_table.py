#!/usr/bin/env python3
import sys
import cv2
import numpy as np

def detect_table_bounds(image):
    """画像内の最も外側の表の枠（矩形）を検出し、四隅の座標を返す"""

    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ノイズ除去（ぼかし）
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # エッジ検出（Canny）
    edges = cv2.Canny(blurred, 50, 150)

    # 輪郭を検出
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 最大の輪郭（表全体の枠）を取得
    largest_contour = max(contours, key=cv2.contourArea)

    # 輪郭を近似（四角形にする）
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)

    if len(approx) != 4:
        print("エラー: 表の枠が四角形として認識されませんでした。", file=sys.stderr)
        sys.exit(1)

    # 四隅の座標を取得（左上、右上、右下、左下）
    rect = sorted(approx[:, 0], key=lambda p: (p[1], p[0]))  # Y優先ソート
    if rect[0][0] > rect[1][0]:
        rect[0], rect[1] = rect[1], rect[0]
    if rect[2][0] > rect[3][0]:
        rect[2], rect[3] = rect[3], rect[2]

    return rect  # [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

def main():
    # 標準入力から画像を受け取る
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

