# Phase 0 — Baseline Audit (2026-09-18)

## 1. Statistik label (`result/label/*`, 1277 file, 0 missing, 0 invalid format)
| kelas | w mean/max | h mean/max | catatan |
|---|---|---|---|
| u_turn (316) | 0.301 / 0.411 | 0.428 / 0.540 | stdev kecil (0.031) = monoton close-up centered, `xc 0.543 yc 0.487` |
| stop (323) | 0.454 / 0.606 | 0.376 / 0.896 | stdev besar (0.136/0.172), `68.7% w>0.5`, min `0.037x0.096` = tidak stabil |
| turn_left (316) | 0.295 / 0.450 | 0.396 / 0.594 | monoton, `xc 0.506 yc 0.520` |
| turn_right (322) | 0.309 / 0.442 | 0.388 / 0.575 | monoton |
| train (1019) | 0.340 / 0.606 | 0.396 / 0.894 | val (258): 0.342 / 0.600, 0.400 / 0.896 |

## 2. Visualisasi expanded (`docs/previews_phase0/grid_*`)
- `u_turn/turn_left/turn_right`: box = **simbol panah dalam**, bukan papan wajik full. 23/24 close-up besar, 1 jauh tapi box longgar ikut background.
- `stop`: **tidak konsisten** — kadang strip teks `STOP` saja, kadang oktagon full, kadang sliver `4%x12%` di tepi (false detect kontur). Ini bug `label_stop.py` (dilate 25x9 + fallback min-max huruf).

## 3. Benchmark ONNX (`models/best.onnx`, stretch ala detect.cpp, conf 0.5)
- 12 gambar (4 example + 8 val): `w mean 38.8% max 53%`, `h mean 40.2% max 58%`, conf 0.88-0.98 (1 val stop 0.458 → no-det).
- Contoh: `example1 turn_right 248x223 (39%x47%) 0.978`, `example3 stop 334x150 (52%x31%) 0.927`.
- Prediksi **mereplikasi cacat GT**: panah dalam / strip teks, bukan papan full (lihat `pred_example1.jpg`, `pred_example3.jpg`).

## 4. Paritas backend
- ORT vs OpenCV DNN (`blobFromImage` stretch) pada 4 example: **MATCH semua** (`dw=0.0 dh=0.0 ds=0.0000`, kelas sama). Patch `fix_onnx_opencv.py` (stride `[1,1,8400]`→`[1,4,8400]`) valid, bukan penyebab.
- Letterbox-inv vs stretch pada `640x480` (r=1.0, pad 80): ukuran sama (`249x223` vs `248x223`). Mismatch preprocessing ada tapi **minor**, bukan akar box full-screen.

## 5. Kesimpulan akar
1. Model belajar box besar karena GT besar + data monoton (semua centered close-up, tanpa jauh/kecil/background).
2. `stop` paling rusak (inkonsisten + false tiny boxes).
3. `detect.cpp` stretch + clamp ke tepi hanya **memperparah visual** saat live dekat, bukan penyebab utama.
4. Klasifikasi benar (conf tinggi) karena head cls mudah; regresi box ikut distribusi GT besar.

## 6. Keputusan yang dibutuhkan sebelum Phase 1
- **Definisi box: full papan rambu** (rekomendasi: wajik full / oktagon full), bukan simbol dalam / strip teks. Semua relabel + retrain mengikuti ini.
- Phase 1: tulis ulang `label_*.py` ke deteksi papan (HSV + poly approx) + audit manual + tambah data jauh/background.
