# Technical Documentation: Dataset Scripts & Auto-Labeling

## Author

name : Brenanda Caesa Pamudya  
email : brenandapamudya178@gmail.com

---

Folder ini berisi source code C++ menggunakan OpenCV untuk pengumpulan sampel dataset gambar rambu/sign dengan resolusi 640x480, serta modul Python untuk anotasi otomatis.

## 1. Script C++ Capture Dataset

Daftar executable dan target direktori gambar mentah:

1. **camera.cpp**
   - Mengambil sampel gambar umum dan menyimpannya ke folder `example/`.
2. **take_u_turn.cpp**
   - Mengambil sampel rambu U-Turn dan menyimpannya ke `result/raw/u_turn/`.
3. **take_stop.cpp**
   - Mengambil sampel rambu STOP dan menyimpannya ke `result/raw/stop/`.
4. **take_turn_left.cpp**
   - Mengambil sampel rambu Belok Kiri dan menyimpannya ke `result/raw/turn_left/`.
5. **take_turn_right.cpp**
   - Mengambil sampel rambu Belok Kanan dan menyimpannya ke `result/raw/turn_right/`.
6. **take_background.cpp**
   - Mengambil sampel background TANPA rambu (meja, lantai, tembok, koridor) ke `result/raw/background/` dan otomatis membuat label `.txt` kosong ke `result/label/background/` (format YOLO background/negatif).

### Konfigurasi Indeks Kamera

Setiap script C++ menyediakan variabel `cameraID` yang dapat disesuaikan pada bagian awal fungsi `main()`:
```cpp
int cameraID = 2; // Ubah ke 0, 1, atau 2 sesuai dengan indeks webcam
```

### Kompilasi

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
g++ -std=c++17 scripts/take_background.cpp -o take_background $(pkg-config --cflags --libs opencv4)
```

### Kontrol Pengoperasian C++

Saat program sedang berjalan pada feed kamera:
- **SPACE** : Toggle Auto-Record Mode (Merekam dan menyimpan frame secara kontinu secepat FPS kamera).
- **s** : Menyimpan 1 frame foto secara manual.
- **q / ESC** : Keluar dari program.

---

## 2. Script Auto-Labeling Python (`scripts/labeling/`)

Sub-direktori `scripts/labeling/` berisi script Python untuk membuat file anotasi bounding box `.txt` format YOLO secara otomatis. Target anotasi adalah **full papan rambu** (wajik penuh / oktagon penuh), bukan simbol di dalamnya:

- **board_utils.py**: Detektor papan bersama (Canny quad + white-fill untuk wajik, mask merah HSV + oktagon untuk STOP) dengan gerbang QC (solidity/aspek/luas) + guard tiny-box. Gambar yang gagal semua QC di-REJECT (tanpa `.txt`, lebih aman dari label palsu).
- **label_u_turn.py / label_stop.py / label_turn_left.py / label_turn_right.py**: Wrapper tipis per kelas.
- **auto_label.py**: Script utama untuk menjalankan keempat proses anotasi otomatis sekaligus + ringkasan OK/REJECT.
- Background (`result/raw/background/`) tidak lewat auto-label: `.txt` kosong dibuat otomatis oleh `take_background`.

### Cara Penggunaan Script Labeling

```bash
# Pastikan virtual environment telah diaktifkan
source nirvana.venv/bin/activate

# Jalankan script auto-labeling utama
python scripts/labeling/auto_label.py
```

---

## 3. Script C++ Real-Time Inference (`scripts/detect.cpp`)

Script C++ untuk melakukan deteksi rambu lalu lintas secara real-time pada feed webcam menggunakan OpenCV DNN dan model `best.onnx`:

- **detect.cpp**
  - Memuat `models/best.onnx` (fallback `best.onnx` di root project).
  - Mengakses webcam via OpenCV VideoCapture (`int cameraID = 2;`).
  - Preprocessing **letterbox** 640x640 (jaga aspek + pad abu-abu, sama seperti training) + inverse-letterbox untuk petakan box ke frame — bukan stretch resize.
  - Parsing tensor output YOLOv8 `[1, 8, 8400]` dan menerapkan Non-Maximum Suppression (NMS).
  - Menggambar bounding box berwarna, label kelas (`u_turn`, `stop`, `turn_left`, `turn_right`), confidence score, ukuran box (% frame), serta perhitungan FPS.
  - Mode headless untuk validasi tanpa kamera: `./detect --image <path> [--save out.jpg]`.

### Catatan kompatibilitas ONNX (penting)
- OpenCV 5.x DNN membalik input `Sub(const, tensor)` → box meledak se-frame walau skor benar. `scripts/fix_onnx_opencv.py` menulis ulang Sub tersebut jadi `Add(const, Neg(tensor))` + verifikasi ekuivalen (maxabsdiff 0.0). Wajib dijalankan ulang setiap terima `best.onnx` baru dari Colab:
  ```bash
  nirvana.venv/bin/python scripts/fix_onnx_opencv.py models/best.onnx
  ```

### Kompilasi dan Eksekusi

```bash
# Kompilasi via Makefile
make detect

# Jalankan pendeteksi real-time (pastikan models/best.onnx sudah ada)
./detect

# Validasi tanpa kamera (gambar statis)
./detect --image example/example1.jpg --save /tmp/out.jpg
```

---

## 4. Split Dataset (`scripts/split_dataset.py`)

Membagi `result/raw` + `result/label` menjadi `dataset/images/{train,val}` dan `dataset/labels/{train,val}` (stratifikasi luas box 80/20, termasuk kelas `background` berlabel kosong), plus validasi tiap pasangan dan `dataset/data.yaml` ber-path relatif:

```bash
nirvana.venv/bin/python scripts/split_dataset.py
```
