import cv2

def draw_rectangle(image_path, output_path, coords):
    """
    指定された画像に赤い矩形を描画し、出力画像として保存する。

    :param image_path: 入力画像のパス
    :param output_path: 出力画像のパス
    :param coords: 矩形の座標（リスト: [x1, y1, x2, y2, x3, y3, x4, y4]）
    """
    # 画像を読み込む
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Error: 画像を読み込めませんでした ({image_path})")

    # 座標を整数に変換
    coords = list(map(int, coords))

    # 矩形のラインを描画（赤色）
    cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), (0, 0, 255), 2)
    cv2.line(image, (coords[2], coords[3]), (coords[4], coords[5]), (0, 0, 255), 2)
    cv2.line(image, (coords[4], coords[5]), (coords[6], coords[7]), (0, 0, 255), 2)
    cv2.line(image, (coords[6], coords[7]), (coords[0], coords[1]), (0, 0, 255), 2)

    # 画像を保存
    cv2.imwrite(output_path, image)

    return output_path  # 出力画像のパスを返す

# スクリプトが直接実行された場合の動作（デバッグ用）
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 11:
        print("Usage: python draw_rectangle.py x1 y1 x2 y2 x3 y3 x4 y4 input.jpg output.jpg")
        sys.exit(1)

    coords = sys.argv[1:9]  # 座標
    input_path = sys.argv[9]
    output_path = sys.argv[10]

    draw_rectangle(input_path, output_path, coords)

