import os
import cv2
import numpy as np

def label_turn_left(raw_dir="result/raw/turn_left", label_dir="result/label/turn_left", class_id=2):
    if not os.path.exists(raw_dir):
        print(f"Directory {raw_dir} not found.")
        return

    os.makedirs(label_dir, exist_ok=True)
    images = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    processed = 0

    for img_name in sorted(images):
        img_path = os.path.join(raw_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        h, w = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_green = np.array([35, 35, 35])
        upper_green = np.array([90, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_box = None
        max_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 1500 and area > max_area:
                bx, by, bw, bh = cv2.boundingRect(cnt)
                max_area = area
                best_box = (bx, by, bw, bh)

        if best_box is None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 3000 and area > max_area:
                    bx, by, bw, bh = cv2.boundingRect(cnt)
                    max_area = area
                    best_box = (bx, by, bw, bh)

        if best_box is not None:
            bx, by, bw, bh = best_box
            x_center = (bx + bw / 2.0) / w
            y_center = (by + bh / 2.0) / h
            w_norm = bw / float(w)
            h_norm = bh / float(h)

            txt_name = os.path.splitext(img_name)[0] + ".txt"
            txt_path = os.path.join(label_dir, txt_name)
            with open(txt_path, "w") as f:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")
            processed += 1

    print(f"turn_left: processed {processed}/{len(images)} labels into {label_dir}")

if __name__ == "__main__":
    label_turn_left()
