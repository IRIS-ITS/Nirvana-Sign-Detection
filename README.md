# Sign Detection Dataset Collector

Program C++ menggunakan OpenCV untuk mengambil dan menyimpan sampel gambar dataset dengan resolusi 640x480 untuk 4 kelas rambu/sign.

## Daftar Script

1. **scripts/take_u_turn.cpp** -> Menyimpan ke `result/u_turn/u_turnX.jpg`
2. **scripts/take_stop.cpp** -> Menyimpan ke `result/stop/stopX.jpg`
3. **scripts/take_turn_left.cpp** -> Menyimpan ke `result/turn_left/turn_leftX.jpg`
4. **scripts/take_turn_right.cpp** -> Menyimpan ke `result/turn_right/turn_rightX.jpg`

## Persyaratan
- Compiler g++ (mendukung C++17)
- Library OpenCV 4

## Cara Kompilasi

Kompilasi semua script sekaligus menggunakan Makefile:
```bash
make
```

Atau kompilasi manual per script:
```bash
g++ -std=c++17 scripts/take_u_turn.cpp -o take_u_turn $(pkg-config --cflags --libs opencv4)
g++ -std=c++17 scripts/take_stop.cpp -o take_stop $(pkg-config --cflags --libs opencv4)
g++ -std=c++17 scripts/take_turn_left.cpp -o take_turn_left $(pkg-config --cflags --libs opencv4)
g++ -std=c++17 scripts/take_turn_right.cpp -o take_turn_right $(pkg-config --cflags --libs opencv4)
```

## Cara Penggunaan

1. Jalankan executable sesuai kelas rambu yang ingin diambil:
   ```bash
   ./take_u_turn
   ./take_stop
   ./take_turn_left
   ./take_turn_right
   ```

2. Kontrol Keyboard:
   - **SPACE** : Toggle Auto FPS Recording (Merekam secara otomatis terus-menerus secepat FPS kamera untuk pengumpulan data cepat). Tekan SPACE sekali untuk mulai (REC), tekan SPACE lagi untuk stop.
   - **s** : Simpan 1 frame foto secara manual.
   - **q** : Keluar dari program.

## Output File
Gambar secara otomatis disimpan pada folder masing-masing kelas:
- `result/u_turn/u_turn<nomor>.jpg`
- `result/stop/stop<nomor>.jpg`
- `result/turn_left/turn_left<nomor>.jpg`
- `result/turn_right/turn_right<nomor>.jpg`
