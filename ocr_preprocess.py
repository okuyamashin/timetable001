import cv2
import numpy as np
import pytesseract
import argparse
import os

# 環境変数を設定（Tesseractが日本語を正しく認識できるようにする）
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata"

def preprocess_image(image_path):
    """罫線を消去し、OCRしやすい画像を作成"""
    # 画像を読み込む（カラー）
    image = cv2.imread(image_path)

    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 罫線を薄くするためのぼかし
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # 二値化（適応的閾値）で文字を強調
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # 罫線をぼかして除去（メディアンフィルタ）
    binary = cv2.medianBlur(binary, 5)

    # 文字を強調するための処理（膨張・収縮）
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.dilate(binary, kernel, iterations=1)
    binary = cv2.erode(binary, kernel, iterations=1)

    return binary

def perform_ocr(image):
    """OCRを実行し、読み取った文字列を返す"""
    text = pytesseract.image_to_string(image, lang="jpn", config="--psm 6")
    return text

def main():
    # 引数の設定
    parser = argparse.ArgumentParser(description="画像から罫線を除去し、OCRを実行する")
    parser.add_argument("image_path", help="OCRを実行する画像ファイルのパス")
    args = parser.parse_args()

    # 画像の前処理
    processed_image = preprocess_image(args.image_path)

    # OCRの実行
    text = perform_ocr(processed_image)

    # 結果を標準出力
    print(text)

if __name__ == "__main__":
    main()

