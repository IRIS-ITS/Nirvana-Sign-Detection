# Sign Detection Dataset Collector

Program C++ menggunakan OpenCV untuk mengambil dan menyimpan sampel gambar dataset dengan resolusi 640x480.

## Persyaratan
- Compiler g++ (mendukung C++17)
- Library OpenCV 4

## Cara Kompilasi

Menggunakan Makefile:
```bash
make
```

Atau kompilasi langsung dengan g++:
```bash
g++ -std=c++17 camera.cpp -o camera $(pkg-config --cflags --libs opencv4)
```

## Cara Penggunaan

1. Jalankan executable yang telah dikompilasi:
   ```bash
   ./camera
   ```

2. Kontrol Keyboard:
   - **s** : Mengambil frame kamera dan menyimpannya ke folder `result/example/` dengan nama `example1.jpg`, `example2.jpg`, dst.
   - **q** : Keluar dari program.

## Output File
Gambar disimpan pada lokasi:
`result/example/example<nomor>.jpg` (ukuran 640x480 piksel).
