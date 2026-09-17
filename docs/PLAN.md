# Sign Detection Model Development Plan

Dokumen perencanaan dan alur kerja pengembangan model deteksi rambu (Sign Detection) 4 kelas menggunakan YOLOv8, ONNX, dan C++ OpenCV DNN.

## Status Dataset saat Ini

Dataset pengumpulan sampel dari 4 kelas rambu telah disimpan pada struktur `result/raw/`:

| Kelas Rambu | Folder Sumber Gambar | Target Label (.txt) | Jumlah Gambar | Class ID |
| :--- | :--- | :--- | :---: | :---: |
| u_turn | result/raw/u_turn/ | result/label/u_turn/ | 316 gambar | 0 |
| stop | result/raw/stop/ | result/label/stop/ | 323 gambar | 1 |
| turn_left | result/raw/turn_left/ | result/label/turn_left/ | 316 gambar | 2 |
| turn_right | result/raw/turn_right/ | result/label/turn_right/ | 322 gambar | 3 |
| **TOTAL** | | | **1.277 gambar** | |

---

## Tahap 1: Anotasi Otomatis (Auto-Labeling) - SELESAI

Telah dibuat script Python di `scripts/labeling/` untuk mendeteksi kontur/bounding box objek rambu secara otomatis pada seluruh 1.277 gambar di `result/raw/`.

Struktur script anotasi:
- `scripts/labeling/label_u_turn.py`
- `scripts/labeling/label_stop.py`
- `scripts/labeling/label_turn_left.py`
- `scripts/labeling/label_turn_right.py`
- `scripts/labeling/auto_label.py`

Output: 1.277 file anotasi `.txt` format YOLO pada `result/label/<class_name>/`.

---

## Tahap 2: Pembagian Dataset (Split Train/Val) - SELESAI

Dataset telah dibagi secara otomatis dengan rasio 80% Train (1.019 gambar) dan 20% Validation (258 gambar) menggunakan script `scripts/split_dataset.py`.

Struktur folder output `dataset/`:
- `dataset/images/train/` (1.019 gambar)
- `dataset/images/val/` (258 gambar)
- `dataset/labels/train/` (1.019 file .txt)
- `dataset/labels/val/` (258 file .txt)
- `dataset/data.yaml`

Konfigurasi `dataset/data.yaml`:
```yaml
path: ./dataset
train: images/train
val: images/val

nc: 4
names:
  0: u_turn
  1: stop
  2: turn_left
  3: turn_right
```

---

## Tahap 3: Pelatihan Model YOLOv8 - TAHAP BERIKUTNYA

Menggunakan arsitektur ringan **YOLOv8n (Nano)** untuk efisiensi dan kecepatan eksekusi pada perangkat robot.

- Framework: PyTorch / Ultralytics YOLOv8.
- Konfigurasi Latihan:
  - Model: `yolov8n.pt`
  - Epochs: 50
  - Image Size: 640x480
  - Data Augmentation: Rotation, Scale, HSV Shift, Flips, Mosaic.

---

## Tahap 4: Ekspor Model ke Format ONNX

Mengonversi bobot pelatihan terbaik (`best.pt`) ke dalam format standar **ONNX** agar dapat dieksekusi secara native pada bahasa C++ tanpa ketergantungan framework PyTorch.

Perintah ekspor:
```bash
yolo export model=best.pt format=onnx imgsz=640
```
Output file: `best.onnx`

---

## Tahap 5: Program Inferensi C++ (Detect Engine)

Membuat program C++ `scripts/detect.cpp` yang menggunakan modul **OpenCV DNN** (`cv::dnn::readNetFromONNX`) untuk inferensi real-time pada feed webcam 640x480.

Alur Kerja C++:
1. Membaca model `best.onnx`.
2. Mengambil frame webcam 640x480.
3. Preprocessing image blob (`cv::dnn::blobFromImage`).
4. Eksekusi model forward pass.
5. Non-Maximum Suppression (NMS) untuk memfilter kotak deteksi berlebih.
6. Menampilkan Bounding Box, Nama Kelas, dan Confidence Score pada window kamera.
