import os
import cv2

from board_utils import accept_box, find_diamond_board, write_yolo_txt

# Target: FULL white diamond board of the TURN-RIGHT sign
# (axis-aligned bbox of the 4-sided board polygon, NOT the inner arrow).


def label_turn_right(raw_dir="result/raw/turn_right", label_dir="result/label/turn_right", class_id=3):
    if not os.path.exists(raw_dir):
        print(f"Directory {raw_dir} not found.")
        return 0, []

    os.makedirs(label_dir, exist_ok=True)
    images = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    processed = 0
    rejected = []

    for img_name in sorted(images):
        img = cv2.imread(os.path.join(raw_dir, img_name))
        if img is None:
            rejected.append(img_name)
            continue

        h, w = img.shape[:2]
        box = find_diamond_board(img)
        if box is None or not accept_box(box, *img.shape[:2][::-1]):
            rejected.append(img_name)
            continue

        write_yolo_txt(os.path.join(label_dir, os.path.splitext(img_name)[0] + ".txt"),
                       class_id, box, w, h)
        processed += 1

    print(f"turn_right: processed {processed}/{len(images)} full-board labels into {label_dir}"
          + (f", rejected {len(rejected)}: {rejected}" if rejected else ""))
    return processed, rejected


if __name__ == "__main__":
    label_turn_right()
