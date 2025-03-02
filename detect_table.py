import cv2
import numpy as np

def detect_table(image_path):
    """ 指定された画像から表の外枠を検出し、4点の座標を返す """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # グレースケールで読み込み
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("Error: No contours found")

    # 最も大きな外枠を検出
    largest_contour = max(contours, key=cv2.contourArea)
    approx = cv2.approxPolyDP(largest_contour, 10, True)

    if len(approx) != 4:
        raise ValueError("Error: Could not find four corners")

    coords = approx.reshape(4, 2)
    return coords.flatten().tolist()  # 8つの数字のリスト

# スクリプト単体実行用 (デバッグ用)
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python detect_table.py <image_path>")
        sys.exit(1)
    
    try:
        coords = detect_table(sys.argv[1])
        print("\t".join(map(str, coords)))  # タブ区切りで出力
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

