import os
import random
import shutil

SIGN_CLASSES = ["u_turn", "stop", "turn_left", "turn_right"]
BG_CLASS = "background"


def _read_label(txt_path):
    """Return (boxes, error). boxes=[] means background (empty file allowed)."""
    try:
        with open(txt_path) as f:
            lines = [l.strip() for l in f if l.strip()]
    except OSError as e:
        return None, str(e)
    boxes = []
    for ln in lines:
        p = ln.split()
        if len(p) != 5:
            return None, f"expected 5 cols, got {len(p)}: {ln}"
        try:
            cid, xc, yc, wn, hn = int(p[0]), float(p[1]), float(p[2]), float(p[3]), float(p[4])
        except ValueError:
            return None, f"non-numeric: {ln}"
        if cid not in (0, 1, 2, 3):
            return None, f"bad class_id {cid}"
        if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 < wn <= 1.0 and 0.0 < hn <= 1.0):
            return None, f"out of range: {ln}"
        boxes.append((cid, xc, yc, wn, hn))
    return boxes, None


def _stratified_split(items, train_ratio, seed):
    """items: list of (key, area). Round-robin per area tercile for balance."""
    rnd = random.Random(seed)
    areas = sorted(a for _, a in items)
    n = len(items)
    t1 = areas[n // 3] if n >= 3 else 0
    t2 = areas[2 * n // 3] if n >= 3 else 0
    bins = [[], [], []]
    for key, area in items:
        bins[0 if area <= t1 else (1 if area <= t2 else 2)].append(key)
    train, val = [], []
    for b in bins:
        rnd.shuffle(b)
        k = int(len(b) * train_ratio)
        train += b[:k]
        val += b[k:]
    return train, val


def split_dataset(
    raw_dir="result/raw",
    label_dir="result/label",
    output_dir="dataset",
    train_ratio=0.8,
    seed=42,
):
    # Build into a temp dir then atomically swap (never half-written dataset)
    tmp_dir = output_dir + ".tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    train_img = os.path.join(tmp_dir, "images", "train")
    val_img = os.path.join(tmp_dir, "images", "val")
    train_lbl = os.path.join(tmp_dir, "labels", "train")
    val_lbl = os.path.join(tmp_dir, "labels", "val")
    for d in (train_img, val_img, train_lbl, val_lbl):
        os.makedirs(d)

    total_train = total_val = 0
    skipped = []

    for cls in SIGN_CLASSES + [BG_CLASS]:
        cls_raw = os.path.join(raw_dir, cls)
        cls_lbl = os.path.join(label_dir, cls)
        if not os.path.exists(cls_raw):
            print(f"Skipping {cls}: {cls_raw} not found")
            continue
        if not os.path.exists(cls_lbl):
            print(f"Skipping {cls}: {cls_lbl} not found")
            continue

        valid = []  # (img_name, area or -1 for bg)
        for img_name in sorted(os.listdir(cls_raw)):
            if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            base = os.path.splitext(img_name)[0]
            src_img = os.path.join(cls_raw, img_name)
            src_txt = os.path.join(cls_lbl, base + ".txt")
            if not os.path.exists(src_txt):
                skipped.append(f"{cls}/{img_name}: missing txt")
                continue
            boxes, err = _read_label(src_txt)
            if err:
                skipped.append(f"{cls}/{base}.txt: {err}")
                continue
            if cls == BG_CLASS:
                if boxes:
                    skipped.append(f"{cls}/{base}.txt: background must be empty")
                    continue
                valid.append((img_name, -1.0))
            else:
                if not boxes:
                    skipped.append(f"{cls}/{base}.txt: sign image with empty label")
                    continue
                area = max(b[3] * b[4] for b in boxes)
                valid.append((img_name, area))

        if cls == BG_CLASS:
            rnd = random.Random(seed)
            names = [v[0] for v in valid]
            rnd.shuffle(names)
            k = int(len(names) * train_ratio)
            train_files, val_files = names[:k], names[k:]
        else:
            train_files, val_files = _stratified_split(valid, train_ratio, seed)

        for img_name in train_files:
            base = os.path.splitext(img_name)[0]
            shutil.copy(os.path.join(cls_raw, img_name), os.path.join(train_img, img_name))
            shutil.copy(os.path.join(cls_lbl, base + ".txt"), os.path.join(train_lbl, base + ".txt"))
            total_train += 1
        for img_name in val_files:
            base = os.path.splitext(img_name)[0]
            shutil.copy(os.path.join(cls_raw, img_name), os.path.join(val_img, img_name))
            shutil.copy(os.path.join(cls_lbl, base + ".txt"), os.path.join(val_lbl, base + ".txt"))
            total_val += 1
        print(f"{cls}: {len(train_files)} train, {len(val_files)} val")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.rename(tmp_dir, output_dir)

    # Relative path -> portable (works locally and on Colab after upload)
    with open(os.path.join(output_dir, "data.yaml"), "w") as f:
        f.write("""path: ./dataset
train: images/train
val: images/val

nc: 4
names:
  0: u_turn
  1: stop
  2: turn_left
  3: turn_right
""")

    print(f"split complete. Total: {total_train} train, {total_val} val into {output_dir}/")
    if skipped:
        print(f"skipped {len(skipped)} (showing max 20):")
        for s in skipped[:20]:
            print(f"  - {s}")


if __name__ == "__main__":
    split_dataset()
