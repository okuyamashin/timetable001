#!/bin/bash

# 入力画像
IMAGE_PATH=$1
OUTPUT_IMAGE="${IMAGE_PATH%.*}_rect.jpeg"  # 例: image.jpeg -> image_output.jpeg
OUTPUT_IMAGE="/tmp/out_rect.jpeg"

# detect_table.py を実行
COORDS=$(cat "$IMAGE_PATH" | python3 detect_table.py)

# エラーチェック
if [ -z "$COORDS" ]; then
    echo "Error: No table detected in $IMAGE_PATH" >&2  # 標準エラー出力
    exit 1
fi

# draw_rectangle.py を実行し、出力画像を指定
python3 draw_rectangle.py $COORDS "$IMAGE_PATH" > "$OUTPUT_IMAGE"
echo "( $COORDS )"
echo "Processing completed. Output saved as: $OUTPUT_IMAGE"

