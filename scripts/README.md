# Technical Documentation: Dataset Capture Scripts

Folder ini berisi source code C++ menggunakan OpenCV untuk pengumpulan sampel dataset gambar rambu/sign dengan resolusi 640x480.

## Daftar Script

1. **camera.cpp**
   - Mengambil sampel gambar umum dan menyimpannya ke folder `example/`.
2. **take_u_turn.cpp**
   - Mengambil sampel rambu U-Turn dan menyimpannya ke folder `result/u_turn/`.
3. **take_stop.cpp**
   - Mengambil sampel rambu STOP dan menyimpannya ke folder `result/stop/`.
4. **take_turn_left.cpp**
   - Mengambil sampel rambu Belok Kiri dan menyimpannya ke folder `result/turn_left/`.
5. **take_turn_right.cpp**
   - Mengambil sampel rambu Belok Kanan dan menyimpannya ke folder `result/turn_right/`.

## Konfigurasi Indeks Kamera

Setiap script menyediakan variabel `cameraID` yang dapat disesuaikan pada bagian awal fungsi `main()`:
```cpp
int cameraID = 2; // Ubah ke 0, 1, atau 2 sesuai dengan indeks webcam
```

## Kompilasi

Kompilasi dapat dilakukan dari root repository menggunakan Makefile:
```bash
make
```

Atau kompilasi manual per script menggunakan g++:
```bash
g++ -std=c++17 scripts/camera.cpp -o camera $(pkg-config --cflags --libs opencv4)
g++ -std=c++17 scripts/take_u_turn.cpp -o take_u_turn $(pkg-config --cflags --libs opencv4)
g++ -std=c++17 scripts/take_stop.cpp -o take_stop $(pkg-config --cflags --libs opencv4)
g++ -std=c++17 scripts/take_turn_left.cpp -o take_turn_left $(pkg-config --cflags --libs opencv4)
g++ -std=c++17 scripts/take_turn_right.cpp -o take_turn_right $(pkg-config --cflags --libs opencv4)
```

## Kontrol Pengoperasian

Saat program sedang berjalan pada feed kamera:
- **SPACE** : Toggle Auto-Record Mode (Merekam dan menyimpan frame secara kontinu secepat FPS kamera).
- **s** : Menyimpan 1 frame foto secara manual.
- **q / ESC** : Keluar dari program.
