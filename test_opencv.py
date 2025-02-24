import cv2
import numpy as np

# 黒い画像を作成
img = np.zeros((300, 300, 3), dtype=np.uint8)

# 白い円を描く
cv2.circle(img, (150, 150), 100, (255, 255, 255), -1)

# 画像を保存
cv2.imwrite("test_circle.png", img)

print("画像 'test_circle.png' を作成しました！")

