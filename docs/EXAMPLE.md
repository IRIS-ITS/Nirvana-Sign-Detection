# Bounding Box Labeling Verification

Dokumen ini berisi sampel visualisasi koordinat bounding box format YOLO yang digambar secara presisi untuk 1 sampel dari masing-masing kelas rambu setelah refactoring auto-labeling presisi.

---

## 1. Class 0: U-Turn (`u_turn1.jpg`)

- File Sumber: `result/raw/u_turn/u_turn1.jpg`
- File Label: `result/label/u_turn/u_turn1.txt`
- Koordinat YOLO Baru: `0 0.540625 0.500000 0.287500 0.412500`
- Ukuran Bounding Box: **28.7% Lebar x 41.2% Tinggi** (Sebelumnya: 62.8% x 84.3%)

![Visualisasi Bounding Box U-Turn](previews/preview_u_turn1.jpg)

---

## 2. Class 1: STOP (`stop1.jpg`)

- File Sumber: `result/raw/stop/stop1.jpg`
- File Label: `result/label/stop/stop1.txt`
- Koordinat YOLO Baru: `1 0.507031 0.509375 0.529687 0.289583`
- Ukuran Bounding Box: **52.9% Lebar x 28.9% Tinggi** (Penggabungan huruf S-T-O-P secara utuh!)

![Visualisasi Bounding Box STOP](previews/preview_stop1.jpg)

---

## 3. Class 2: Turn Left (`turn_left1.jpg`)

- File Sumber: `result/raw/turn_left/turn_left1.jpg`
- File Label: `result/label/turn_left/turn_left1.txt`
- Koordinat YOLO Baru: `2 0.472656 0.502083 0.248438 0.333333`
- Ukuran Bounding Box: **24.8% Lebar x 33.3% Tinggi** (Sebelumnya: 55.1% x 72.0%)

![Visualisasi Bounding Box Turn Left](previews/preview_turn_left1.jpg)

---

## 4. Class 3: Turn Right (`turn_right1.jpg`)

- File Sumber: `result/raw/turn_right/turn_right1.jpg`
- File Label: `result/label/turn_right/turn_right1.txt`
- Koordinat YOLO Baru: `3 0.492969 0.519792 0.257812 0.347917`
- Ukuran Bounding Box: **25.7% Lebar x 34.7% Tinggi** (Sebelumnya: 57.3% x 75.4%)

![Visualisasi Bounding Box Turn Right](previews/preview_turn_right1.jpg)
