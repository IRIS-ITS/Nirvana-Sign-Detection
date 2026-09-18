# Training Notebook (`notebooks/`)

name : Brenanda Caesa Pamudya
email : brenandapamudya178@gmail.com

## Isi

- **01_Training_Sign.ipynb** — Alur lengkap training YOLOv8n (4 kelas rambu, label full-papan): setup → resolve `dataset/data.yaml` → load `yolov8n.pt` → train → val + gate → export ONNX + patch OpenCV → download artifacts.

## Cara Pakai (Google Colab, wajib GPU)

1. Runtime → Change runtime type → **T4 GPU**.
2. Upload / `git pull` repo versi terbaru (berisi split `dataset/` 1778 train / 452 val), buka notebook, **Run All** (±30-60 menit).
3. Cell 1 memberi warning bila tanpa GPU — jangan lanjut training di CPU.
4. Perhatikan **GATE** di cell validasi: `mAP50 > 0.90` = PASS. Jika FAIL, jangan export — perbaiki data dulu (tambah capture / cek label).
5. Download `best.onnx` (+ `best.pt` sebagai backup), taruh `best.onnx` ke `models/` di mesin lokal.

## Konfigurasi Training (Phase 4)

`epochs=100, patience=20, imgsz=640, batch=16, seed=42`, augmentasi `scale=0.5, fliplr=0.5, degrees=15, hsv(0.015/0.7/0.4), mosaic=1.0, close_mosaic=10`.

## Setelah Download

Wajib patch kompatibilitas sebelum dipakai `detect` (OpenCV DNN salah membaca sebagian graph tanpa ini):

```bash
nirvana.venv/bin/python scripts/fix_onnx_opencv.py models/best.onnx
```

Hasil training (`runs/`, `*.pt`) tidak di-push (lihat `.gitignore`); yang di-push hanya config notebook dan dataset.
