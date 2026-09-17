# Roadmap Perbaikan Sign Detection (akar → hilir)

Sumber masalah (Phase 0, `docs/PHASE0_BASELINE.md`): GT box besar + data monoton
close-up → model belajar box besar → `detect.cpp` stretch + clamp memperparah
visual full-screen. Klasifikasi benar (conf 0.9+) karena head cls mudah.

Legenda status: ✅ selesai · ⬜ belum · 🔄 berjalan

---

## Phase 0 — Audit baseline ✅
- Statistik semua label (`result/label/*`, 1277 file): mean/side-frac, missing/orphan.
- Visualisasi expanded 20-30 sampel/kelas → `docs/previews_phase0/grid_*.jpg`.
- Benchmark `best.onnx` via onnxruntime (stretch ala `detect.cpp`) di
  `example/*.jpg` + `dataset/images/val` → catat cx,cy,w,h,conf.
- Paritas onnxruntime vs OpenCV DNN pada gambar statis yang sama.
- Uji letterbox-inverse vs stretch (terbukti minor untuk 640x480).
- Hasil: `docs/PHASE0_BASELINE.md`. Keputusan: definisi box = **full papan**.

## Phase 1 — Relabel full-board ✅
- `scripts/labeling/board_utils.py` (baru): `find_diamond_board()` / `find_stop_board()`.
- Tulis ulang `label_{u_turn,stop,turn_left,turn_right}.py` + `auto_label.py`
  (lapor OK/REJECT; reject = tanpa `.txt`, lebih aman dari label palsu).
- Backup: `result/label_phase0_backup/`. Bukti: `docs/previews_phase1/`,
  laporan `docs/PHASE1_RELABEL.md`. Hasil: 1277/1277, 0 reject.

## Phase 2 — Diversifikasi data 🔄 (capture jauh/sedang masuk 2048 img, label 2047 OK)
> Detail: `docs/PHASE2_DATA.md`. Sisa: `background/` 50-100 gambar.
Tujuan: model kenal objek jauh/kecil/miring + background kosong.
1. Capture baru via `take_*` (640x480): per kelas wajib ada porsi
   jauh (box <15%), sedang (15-35%), dekat (35-60%), angle ±30°,
   lighting pagi/siang/mendung, background beda.
2. Tambah `result/raw/background/` 50-100 gambar tanpa rambu (meja, lantai,
   tembok, koridor) + label `.txt` kosong.
3. Relabel otomatis (`auto_label.py`) + audit grid ulang.
   Kriteria lolos: tiap kelas punya sebaran area (tidak menumpuk di >40%),
   background 100% kosong terdeteksi nol box.
   Perintah:
   ```bash
   nirvana.venv/bin/python scripts/labeling/auto_label.py
   ```

## Phase 3 — Split robust ⬜
File: `scripts/split_dataset.py`, output `dataset/` + `dataset/data.yaml`.
1. Hapus `rmtree` brutal → rebuild aman; validasi tiap pasangan
   (img ada + txt ada + isi 5 kolom + nilai 0-1); dukung `.txt` kosong
   (background) ikut tersalin.
2. Stratifikasi ukuran box saat split 80/20 + sertakan background di train/val.
3. `data.yaml` pakai `path: ./dataset` relatif (bukan absolut).
   Perintah:
   ```bash
   nirvana.venv/bin/python scripts/split_dataset.py
   ```
   Kriteria: `train ~80% + val ~20%`, hitung ulang statistik tidak timpang,
   tidak ada gambar tanpa pasangan valid.

## Phase 4 — Retrain YOLOv8n ⬜
File: `notebooks/01_Training_Sign.ipynb`. Output: `runs/detect/sign_detection/`.
1. Config: `yolov8n.pt, imgsz=640, epochs 80-100, batch 16, patience 20`,
   augmentasi `mosaic, scale 0.5-1.5, hsv, fliplr 0.5, degrees 15`.
2. Wajib simpan `mAP50, mAP50-95, confusion_matrix, F1-curve, val/predict`
   di `runs/` (jangan hanya di Colab).
3. Gate: `mAP50 >0.90` DAN cek visual `val/predict` box tight full-papan.
   Kalau di Python masih lebar → data belum beres, jangan export.

## Phase 5 — Export + validasi ONNX ⬜
File: `scripts/fix_onnx_opencv.py`. Output: `models/best.onnx` (satu sumber).
1. `export format=onnx, imgsz=640, opset=12, simplify=True`.
2. Perkuat `fix_onnx`: verifikasi output before/after patch via onnxruntime
   (max diff `<1e-4`), jangan silent-hardcode.
3. Hapus duplikat `best.onnx` di root; `detect.cpp` hanya load satu path.
4. Paritas ulang ORT vs OpenCV DNN (acuan Phase 0: `dw<5px, ds<0.05`).

## Phase 6 — Fix `detect.cpp` ⬜
File: `scripts/detect.cpp` (fungsi: `:69` blob, `:92-93` scale, `:120-123` clamp).
1. Ganti stretch → **letterbox** (`r=min(640/W,640/H)`, pad 114) persis training.
2. Scale balik inverse-letterbox: `x=(cx-pad_x)/r`, `w=w_pred/r` → ke frame.
3. Enforce resize frame aktual 640x480 + tolak frame kosong; filter anomali
   `w,h >85%` frame; opsional shrink visual 2-3%.
4. Tampilkan `%w x %h` untuk debug live. Build: `make detect`.
   Kriteria: objek kecil → box kecil mengikuti; tidak nempel tepi.

## Phase 7 — Acceptance test ⬜
1. Statis: semua `example/*.jpg` box `<50%` + melingkari papan penuh.
2. Live `./detect` dekat/jauh: box mengikuti ukuran objek.
3. Simpan video before/after + tulis `docs/ACCEPTANCE.md` (angka + tanggal).

---
Riwayat: Phase 0 (`docs/PHASE0_BASELINE.md`), Phase 1 (`docs/PHASE1_RELABEL.md`).
Master plan ini (ROADMAP) adalah acuan tunggal; per-phase detail menyusul
di file masing-masing saat dikerjakan.
