import cv2
import numpy as np

def detect_table(image_path):
    """
    指定された画像から表の外枠を検出し、4点の座標を返す
    :param image_path: 入力画像のパス
    :return: 矩形の座標リスト [x1, y1, x2, y2, x3, y3, x4, y4]
    """
    # 画像を読み込み（グレースケール）
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # コントラストを上げるために前処理
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)

    # 輪郭を検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("Error: No contours found")

    # 面積が最大の輪郭（表全体）を取得
    largest_contour = max(contours, key=cv2.contourArea)

    # 輪郭を近似（できるだけ矩形に）
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)

    # 近似結果が四角形でない場合はエラー
    if len(approx) != 4:
        raise ValueError("Error: Could not find four corners")

    # 4点の座標を取得
    coords = approx.reshape(4, 2)
    
    # 左上・右上・右下・左下の順に並べる
    sorted_coords = sorted(coords, key=lambda p: (p[1], p[0]))  # Y座標優先でソート
    top_coords = sorted(sorted_coords[:2], key=lambda p: p[0])  # 上部2点をX座標でソート
    bottom_coords = sorted(sorted_coords[2:], key=lambda p: p[0])  # 下部2点をX座標でソート

    final_coords = np.array([top_coords[0], top_coords[1], bottom_coords[1], bottom_coords[0]])

    return final_coords.flatten().tolist()  # 8つの数値のリスト

# デバッグ用
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python detect_table.py <image_path>")
        sys.exit(1)

    try:
        coords = detect_table(sys.argv[1])
        print("\t".join(map(str, coords)))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

