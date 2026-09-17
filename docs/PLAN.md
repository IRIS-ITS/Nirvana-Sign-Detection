# Sign Detection Model Development Plan

Dokumen perencanaan dan alur kerja pengembangan model deteksi rambu (Sign Detection) 4 kelas menggunakan YOLOv8, ONNX, dan C++ OpenCV DNN.

## Status Dataset saat Ini

Dataset pengumpulan sampel dari 4 kelas rambu telah berhasil dikumpulkan dengan rincian:

| Kelas Rambu | Folder Sumber | Jumlah Gambar | Class ID |
| :--- | :--- | :---: | :---: |
| u_turn | result/u_turn/ | 316 gambar | 0 |
| stop | result/stop/ | 323 gambar | 1 |
| turn_left | result/turn_left/ | 316 gambar | 2 |
| turn_right | result/turn_right/ | 322 gambar | 3 |
| **TOTAL** | | **1.277 gambar** | |

---

## Tahap 1: Anotasi Otomatis (Auto-Labeling)

Membuat script Python `scripts/auto_label.py` menggunakan OpenCV contour detection untuk mendeteksi kontur objek rambu secara otomatis pada seluruh 1.277 gambar di `result/`.

- Output: File anotasi `.txt` format YOLO pada tiap gambar:
  `<class_id> <x_center> <y_center> <width> <height>` (normalized 0.0 - 1.0).

---

## Tahap 2: Pembagian Dataset (Split Train/Val)

Membagi dataset secara otomatis dengan rasio 80% data latihan (Train) dan 20% data validasi (Validation).

Struktur folder output `dataset/`:
```text
dataset/
├── images/
│   ├── train/  (~1.020 gambar)
│   └── val/    (~257 gambar)
├── labels/
│   ├── train/  (~1.020 file .txt)
│   └── val/    (~257 file .txt)
└── data.yaml
```

Konfigurasi `data.yaml`:
```yaml
path: ./dataset
train: images/train
val: images/val
nc: 4
names: ['u_turn', 'stop', 'turn_left', 'turn_right']
```

---

## Tahap 3: Pelatihan Model YOLOv8

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
