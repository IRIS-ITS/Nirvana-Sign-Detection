# Nirvana Sign Detection

Repository untuk pengumpulan dataset dan pengembangan model deteksi rambu (Sign Detection) berbasis C++ dan OpenCV.

## Deskripsi Project

Project ini dirancang untuk mendeteksi 4 jenis kelas rambu:
1. **u_turn**: Rambu Putar Balik
2. **stop**: Rambu STOP
3. **turn_left**: Rambu Belok Kiri
4. **turn_right**: Rambu Belok Kanan

## Struktur Direktori

- **scripts/**: Berisi source code C++ untuk akuisisi dataset via webcam (`camera.cpp`, `take_u_turn.cpp`, `take_stop.cpp`, `take_turn_left.cpp`, `take_turn_right.cpp`).
- **example/**: Folder penyimpanan sampel gambar umum pengujian.
- **result/**: Folder penyimpanan dataset yang dikelompokkan berdasarkan kelas rambu (`u_turn/`, `stop/`, `turn_left/`, `turn_right/`).
- **dataset/**: Folder penampung dataset yang sudah diformat untuk pelatihan model.
- **notebooks/**: Folder jupyter notebook untuk eksperimen dan pelatihan model.
- **docs/**: Dokumentasi tambahan project.
- **Makefile**: File otomasi kompilasi seluruh source code C++.

## Panduan Ringkas

1. Kompilasi seluruh program:
   ```bash
   make
   ```

2. Jalankan executable pengambil dataset sesuai kebutuhan:
   ```bash
   ./take_u_turn     # Pengumpulan sampel U-Turn
   ./take_stop       # Pengumpulan sampel STOP
   ./take_turn_left  # Pengumpulan sampel Belok Kiri
   ./take_turn_right # Pengumpulan sampel Belok Kanan
   ```

Untuk petunjuk teknis pengoperasian script, penggunaan tombol keyboard, dan pengaturan indeks kamera, silakan baca dokumentasi teknis pada [scripts/README.md](scripts/README.md).
