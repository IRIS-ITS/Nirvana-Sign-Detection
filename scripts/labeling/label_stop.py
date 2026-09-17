import os
import cv2
import numpy as np

def label_stop(raw_dir="result/raw/stop", label_dir="result/label/stop", class_id=1):
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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Dilation kernel to connect individual letters S-T-O-P into a single unified bounding box
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 9))
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        best_box = None
        max_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            bx, by, bw, bh = cv2.boundingRect(cnt)
            if 0.10 * w < bw < 0.85 * w and 0.08 * h < bh < 0.70 * h and area > 500:
                aspect = bw / float(bh)
                if 0.5 < aspect < 5.0 and area > max_area:
                    max_area = area
                    best_box = (bx, by, bw, bh)

        # Method 2: Combine bounding boxes of individual detected letters (S, T, O, P)
        if best_box is None:
            contours_raw, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            letter_boxes = []
            for cnt in contours_raw:
                area = cv2.contourArea(cnt)
                bx, by, bw, bh = cv2.boundingRect(cnt)
                if 0.03 * w < bw < 0.40 * w and 0.08 * h < bh < 0.60 * h and area > 150:
                    letter_boxes.append((bx, by, bw, bh))
            if letter_boxes:
                min_x = min(b[0] for b in letter_boxes)
                min_y = min(b[1] for b in letter_boxes)
                max_x = max(b[0] + b[2] for b in letter_boxes)
                max_y = max(b[1] + b[3] for b in letter_boxes)
                best_box = (min_x, min_y, max_x - min_x, max_y - min_y)

        # Method 3: Fallback to adaptive thresholding
        if best_box is None:
            thresh_adapt = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            contours_adapt, _ = cv2.findContours(thresh_adapt, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours_adapt:
                area = cv2.contourArea(cnt)
                bx, by, bw, bh = cv2.boundingRect(cnt)
                if 0.08 * w < bw < 0.60 * w and 0.08 * h < bh < 0.60 * h and area > max_area:
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

    print(f"stop: processed {processed}/{len(images)} labels into {label_dir}")

if __name__ == "__main__":
    label_stop()
