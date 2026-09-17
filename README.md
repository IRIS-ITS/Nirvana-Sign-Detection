# Nirvana Sign Detection

Repository untuk pengumpulan dataset dan pengembangan model deteksi rambu (Sign Detection) berbasis C++ dan OpenCV.

## Deskripsi Project

Project ini dirancang untuk mendeteksi 4 jenis kelas rambu:
1. **u_turn**: Rambu Putar Balik
2. **stop**: Rambu STOP
3. **turn_left**: Rambu Belok Kiri
4. **turn_right**: Rambu Belok Kanan

## Struktur Direktori

- **scripts/**: Berisi source code C++ untuk akuisisi dataset via webcam dan sub-direktori `scripts/labeling/` untuk script auto-labeling Python.
- **example/**: Folder penyimpanan sampel gambar umum pengujian.
- **result/**: Folder penampung data hasil akuisisi yang terbagi menjadi:
  - `result/raw/`: Tempat tersimpannya gambar mentah hasil akuisisi kamera per kelas.
  - `result/label/`: Tempat tersimpannya file anotasi `.txt` format YOLO hasil auto-labeling.
- **dataset/**: Folder penampung dataset yang sudah diformat untuk pelatihan model (split train/val).
- **notebooks/**: Folder jupyter notebook untuk eksperimen dan pelatihan model.
- **docs/**: Dokumentasi tambahan project (`PLAN.md`).
- **requirements.txt**: Daftar dependensi modul Python untuk ekosistem pelatihan dan pemrosesan dataset.
- **Makefile**: File otomasi kompilasi seluruh source code C++.

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

## Panduan Kompilasi & Pengoperasian C++

1. Kompilasi seluruh program:
   ```bash
   make
   ```

2. Jalankan executable pengambil dataset sesuai kebutuhan:
   ```bash
   ./take_u_turn     # Pengumpulan sampel U-Turn ke result/raw/u_turn/
   ./take_stop       # Pengumpulan sampel STOP ke result/raw/stop/
   ./take_turn_left  # Pengumpulan sampel Belok Kiri ke result/raw/turn_left/
   ./take_turn_right # Pengumpulan sampel Belok Kanan ke result/raw/turn_right/
   ```

Untuk petunjuk teknis pengoperasian script, penggunaan tombol keyboard, dan pengaturan indeks kamera, silakan baca dokumentasi teknis pada [scripts/README.md](scripts/README.md).
