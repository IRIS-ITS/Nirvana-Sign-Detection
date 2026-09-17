import os
import cv2
import numpy as np

def visualize_samples(out_dir="docs/previews"):
    os.makedirs(out_dir, exist_ok=True)
    classes = [("u_turn", 0, (255, 255, 0)), 
               ("stop", 1, (0, 0, 255)), 
               ("turn_left", 2, (0, 255, 255)), 
               ("turn_right", 3, (0, 255, 0))]

    print("Generating label visualization samples...")
    for c_name, c_id, color in classes:
        raw_dir = os.path.join("result/raw", c_name)
        label_dir = os.path.join("result/label", c_name)
        if not os.path.exists(raw_dir) or not os.path.exists(label_dir):
            continue

        raw_imgs = sorted([f for f in os.listdir(raw_dir) if f.endswith(".jpg")])
        if not raw_imgs:
            continue

        img_name = raw_imgs[0] # Pick first image of each class
        img_path = os.path.join(raw_dir, img_name)
        txt_path = os.path.join(label_dir, os.path.splitext(img_name)[0] + ".txt")

        if not os.path.exists(txt_path):
            continue

        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        with open(txt_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                cid, xc, yc, wn, hn = map(float, parts)
                bx = int((xc - wn / 2.0) * w)
                by = int((yc - hn / 2.0) * h)
                bw = int(wn * w)
                bh = int(hn * h)

                # Draw bounding box
                cv2.rectangle(img, (bx, by), (bx + bw, by + bh), color, 2)
                label_str = f"{c_name} ({wn*100:.1f}%x{hn*100:.1f}%)"
                cv2.rectangle(img, (bx, by - 22), (bx + len(label_str)*10 + 10, by), color, -1)
                cv2.putText(img, label_str, (bx + 5, by - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        out_path = os.path.join(out_dir, f"preview_{c_name}1.jpg")
        cv2.imwrite(out_path, img)
        print(f"Saved visualization preview: {out_path}")

if __name__ == "__main__":
    visualize_samples()
