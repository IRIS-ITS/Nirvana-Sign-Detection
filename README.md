# Nirvana Sign Detection

Repository untuk pengumpulan dataset dan pengembangan model deteksi rambu (Sign Detection) berbasis C++ dan OpenCV.

## Deskripsi Project

Project ini dirancang untuk mendeteksi 4 jenis kelas rambu (bounding box = **full papan rambu**):
1. **u_turn**: Rambu Putar Balik (wajik penuh)
2. **stop**: Rambu STOP (oktagon penuh)
3. **turn_left**: Rambu Belok Kiri (wajik penuh)
4. **turn_right**: Rambu Belok Kanan (wajik penuh)

Dataset saat ini: ±2048 gambar rambu (dekat/sedang/jauh) + 183 gambar background negatif, split 1778 train / 452 val.

## Struktur Direktori

- **scripts/**: Source code C++ akuisisi dataset via webcam (`take_*`), sub-direktori `scripts/labeling/` untuk auto-labeling Python full-papan, `split_dataset.py`, `fix_onnx_opencv.py`, dan `detect.cpp` untuk inferensi real-time.
- **example/**: Sampel gambar umum pengujian.
- **result/**: Data hasil akuisisi yang terbagi menjadi:
  - `result/raw/`: Gambar mentah kamera per kelas (`u_turn/`, `stop/`, `turn_left/`, `turn_right/`, `background/`).
  - `result/label/`: File anotasi `.txt` format YOLO hasil auto-labeling (`.txt` kosong = background).
- **dataset/**: Dataset terformat untuk training (split train/val + `data.yaml`).
- **models/**: Model ONNX siap pakai (`models/best.onnx`).
- **notebooks/**: Jupyter notebook eksperimen dan pelatihan model (YOLOv8n, GPU Colab).
- **docs/**: Dokumentasi dan laporan audit lokal (tidak di-push, lihat `.gitignore`).
- **requirements.txt**: Dependensi Python untuk training dan pemrosesan dataset.
- **Makefile**: Otomasi kompilasi seluruh source code C++.

## Panduan Pengaturan Lingkungan Python

Pastikan untuk membuat file virtual environment agar package terisolasi:

```bash
python3 -m venv nirvana.venv --system-site-packages
```

Untuk mengaktifkan virtual environment `nirvana.venv` dan menginstal seluruh modul yang dibutuhkan:

```bash
# Mengaktifkan virtual environment
source nirvana.venv/bin/activate

# Menginstal dependensi Python
pip install -r requirements.txt
```

## Alur Kerja Singkat

```bash
# 1. Ambil gambar (s = simpan 1 frame, SPACE = auto-record, q = keluar)
./take_u_turn | ./take_stop | ./take_turn_left | ./take_turn_right | ./take_background

# 2. Auto-labeling full-papan (background dilewati, .txt kosong sudah otomatis)
nirvana.venv/bin/python scripts/labeling/auto_label.py

# 3. Split train/val
nirvana.venv/bin/python scripts/split_dataset.py

# 4. Training di Google Colab (GPU) via notebooks/01_Training_Sign.ipynb,
#    download best.onnx hasilnya ke models/, lalu patch kompatibilitas:
nirvana.venv/bin/python scripts/fix_onnx_opencv.py models/best.onnx

# 5. Deteksi real-time / uji gambar statis
./detect
./detect --image example/example1.jpg --save /tmp/out.jpg
```

> Penting: setiap menerima `best.onnx` baru dari Colab, wajib jalankan `fix_onnx_opencv.py` (OpenCV DNN salah mengartikan sebagian graph tanpa patch).

## Panduan Kompilasi & Pengoperasian C++

1. Kompilasi seluruh program:
   ```bash
   make
   ```

2. Jalankan executable pengambil dataset atau pendeteksi real-time sesuai kebutuhan:
   ```bash
   ./take_u_turn     # Pengumpulan sampel U-Turn ke result/raw/u_turn/
   ./take_stop       # Pengumpulan sampel STOP ke result/raw/stop/
   ./take_turn_left  # Pengumpulan sampel Belok Kiri ke result/raw/turn_left/
   ./take_turn_right # Pengumpulan sampel Belok Kanan ke result/raw/turn_right/
   ./take_background # Sampel background (tanpa rambu) + label .txt kosong otomatis
   ./detect          # Pendeteksi rambu real-time (menggunakan models/best.onnx)
   ```

Untuk petunjuk teknis pengoperasian script, penggunaan tombol keyboard, dan pengaturan indeks kamera, silakan baca dokumentasi teknis pada [scripts/README.md](scripts/README.md).
