import cv2
import numpy as np
import os
import sys

from collections import defaultdict

def process_matching_results(results):
    """
    テンプレートマッチング結果を加工し、各店舗ごとに最大スコアのエントリを取得。
    
    :param results: [(filename, score, top_left, bottom_right), ...] のリスト
    :return: [(store_name, score, top_y_coordinate)]
    """
    if not results:
        return []

    store_best_matches = defaultdict(lambda: (None, float('-inf'), None))

    for filename, score, top_left, bottom_right in results:
        store_name = os.path.splitext(filename)[0].split("_")[-1]  # 最後の要素が店舗名
        top_y_coordinate = top_left[1]  # Y座標 (top_left[1])

        # その店舗のスコア最大のエントリを保持
        if score > store_best_matches[store_name][1]:  # 現在の最大スコアより高ければ更新
            store_best_matches[store_name] = (store_name, score, top_y_coordinate)

    # 各店舗の最大スコアエントリをリストに変換
    return list(store_best_matches.values())


def preprocess_image(image_path):
    """ 画像をグレースケール変換し、バイナリ化 """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    return thresh

def template_matching(target, template):
    """ テンプレートマッチングを使用してスコア計算と座標取得 """
    res = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # テンプレートサイズを取得
    h, w = template.shape[:2]
    top_left = max_loc  # 最大値の座標（左上）
    bottom_right = (top_left[0] + w, top_left[1] + h)  # 右下

    return max_val, top_left, bottom_right

def compare_to_directory(target_image_path, directory_path, visualize=False):
    """ ターゲット画像をディレクトリ内の画像と比較し、スコアと座標を出力 """
    target_image = preprocess_image(target_image_path)
    scores = []
    
    for filename in os.listdir(directory_path):
        template_path = os.path.join(directory_path, filename)
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue  # 画像以外はスキップ

        template_image = preprocess_image(template_path)
        score_tm, top_left, bottom_right = template_matching(target_image, template_image)

        scores.append((filename, score_tm, top_left, bottom_right))

        # 検出位置を描画（オプション）
        if visualize and score_tm > 0.5:  # しきい値以上のみ表示
            target_color = cv2.imread(target_image_path)
            cv2.rectangle(target_color, top_left, bottom_right, (0, 255, 0), 2)
            cv2.imshow(f"Match: {filename}", target_color)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    # スコアが高い順にソート
    scores.sort(key=lambda x: x[1], reverse=True)

    return scores

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python store_recognition.py <image_path>")
        sys.exit(1)

    target_image_path = sys.argv[1]

    directory_path = "/var/www/html/opencv/store_template/"  # 既知の店舗名画像が入っているディレクトリ

    results = compare_to_directory(target_image_path, directory_path)

    processed_results = process_matching_results(results)
    print(processed_results)

