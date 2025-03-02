#!/usr/bin/env python3
import sys
import os
import cv2
import numpy as np

def rotate_image(input_stream, angle):
    # 入力データをバイト列として読み取る
    img_bytes = input_stream.read()
    
    # NumPy 配列に変換
    np_arr = np.frombuffer(img_bytes, np.uint8)
    
    # OpenCV で画像をデコード
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        print("エラー: 画像の読み込みに失敗しました。", file=sys.stderr)
        sys.exit(1)

    # 回転処理
    if angle == 90:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif angle == 270:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    return img

def main():
    # 引数チェック
    if len(sys.argv) != 2:
        print("使い方: python rotate.py <角度(0, 90, 180, 270)>", file=sys.stderr)
        sys.exit(1)

    # 角度を取得
    try:
        angle = int(sys.argv[1])
        if angle not in {0, 90, 180, 270}:
            raise ValueError
    except ValueError:
        print("エラー: 角度は 0, 90, 180, 270 のいずれかを指定してください。", file=sys.stderr)
        sys.exit(1)

    # 標準入力から画像を受け取る
    img = rotate_image(sys.stdin.buffer, angle)

    # 標準出力に書き込めるかチェック
    if sys.stdout.isatty():
        # 標準出力が使えない場合は、ファイルとして保存
        input_filename = "output"
        output_filename = f"{input_filename}.{angle}.jpeg"
        cv2.imwrite(output_filename, img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        print(f"画像を {output_filename} に保存しました。")
    else:
        # 標準出力に書き込む
        _, buffer = cv2.imencode(".jpeg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        sys.stdout.buffer.write(buffer.tobytes())

if __name__ == "__main__":
    main()

