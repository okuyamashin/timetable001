#!/usr/bin/env python3
import sys
import cv2
import numpy as np

def draw_rectangle(image, corners):
    """指定された4点を結ぶ赤い矩形を画像に描画"""
    pts = np.array(corners, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(image, [pts], isClosed=True, color=(0, 0, 255), thickness=3)  # 赤枠

    return image

def main():
    # コマンドライン引数から 8 つの数値を取得
    if len(sys.argv) != 9:
        print("使い方: python draw_rectangle.py x1 y1 x2 y2 x3 y3 x4 y4", file=sys.stderr)
        sys.exit(1)

    try:
        coords = list(map(int, sys.argv[1:]))
    except ValueError:
        print("エラー: すべての引数は整数である必要があります。", file=sys.stderr)
        sys.exit(1)

    # 座標リストを作成
    corners = [(coords[i], coords[i+1]) for i in range(0, 8, 2)]

    # 標準入力から画像を受け取る
    img_bytes = sys.stdin.buffer.read()
    np_arr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        print("エラー: 画像の読み込みに失敗しました。", file=sys.stderr)
        sys.exit(1)

    # 矩形を描画
    result_image = draw_rectangle(image, corners)

    # 標準出力に書き出し
    _, buffer = cv2.imencode(".jpeg", result_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    sys.stdout.buffer.write(buffer.tobytes())

if __name__ == "__main__":
    main()

