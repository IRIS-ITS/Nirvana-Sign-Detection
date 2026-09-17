import os
import random
import shutil

def split_dataset(
    raw_dir="result/raw",
    label_dir="result/label",
    output_dir="dataset",
    train_ratio=0.8,
    seed=42
):
    random.seed(seed)
    classes = ["u_turn", "stop", "turn_left", "turn_right"]

    train_img_dir = os.path.join(output_dir, "images", "train")
    val_img_dir = os.path.join(output_dir, "images", "val")
    train_lbl_dir = os.path.join(output_dir, "labels", "train")
    val_lbl_dir = os.path.join(output_dir, "labels", "val")

    # Clean existing dataset directory to remove old labels and images
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    for d in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
        os.makedirs(d, exist_ok=True)

    total_train = 0
    total_val = 0

    for cls in classes:
        cls_raw_dir = os.path.join(raw_dir, cls)
        cls_lbl_dir = os.path.join(label_dir, cls)

        if not os.path.exists(cls_raw_dir) or not os.path.exists(cls_lbl_dir):
            print(f"Skipping {cls}: directory not found")
            continue

        images = [f for f in os.listdir(cls_raw_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(images)

        split_idx = int(len(images) * train_ratio)
        train_files = images[:split_idx]
        val_files = images[split_idx:]

        for img_name in train_files:
            base_name = os.path.splitext(img_name)[0]
            txt_name = base_name + ".txt"

            src_img = os.path.join(cls_raw_dir, img_name)
            src_txt = os.path.join(cls_lbl_dir, txt_name)

            if os.path.exists(src_img) and os.path.exists(src_txt):
                shutil.copy(src_img, os.path.join(train_img_dir, img_name))
                shutil.copy(src_txt, os.path.join(train_lbl_dir, txt_name))
                total_train += 1

        for img_name in val_files:
            base_name = os.path.splitext(img_name)[0]
            txt_name = base_name + ".txt"

            src_img = os.path.join(cls_raw_dir, img_name)
            src_txt = os.path.join(cls_lbl_dir, txt_name)

            if os.path.exists(src_img) and os.path.exists(src_txt):
                shutil.copy(src_img, os.path.join(val_img_dir, img_name))
                shutil.copy(src_txt, os.path.join(val_lbl_dir, txt_name))
                total_val += 1

        print(f"{cls}: {len(train_files)} train, {len(val_files)} val")

    # Generate data.yaml configuration file using absolute path
    abs_output_dir = os.path.abspath(output_dir)
    yaml_path = os.path.join(output_dir, "data.yaml")
    yaml_content = f"""path: {abs_output_dir}
train: images/train
val: images/val

nc: 4
names:
  0: u_turn
  1: stop
  2: turn_left
  3: turn_right
"""
    with open(yaml_path, "w") as f:
        f.write(yaml_content)

    print(f"split complete. Total: {total_train} train, {total_val} val into {output_dir}/")
    print(f"data.yaml written to {yaml_path}")

if __name__ == "__main__":
    split_dataset()
