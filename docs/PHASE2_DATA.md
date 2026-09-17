# Phase 2 — Data Baru: Audit & Relabel (2026-09-18)

## 1. Data masuk
- u_turn 316→513 (+197), stop 323→531 (+208), turn_left 316→503 (+187),
  turn_right 322→501 (+179). Total raw 1277→2048. Semua terbaca.
- `result/raw/background/` masih kosong — belum diambil user.

## 2. Temuan saat relabel (detektor Phase 1 + perbaikan)
- Jalan 1: 88 gambar stop baru REJECT. Penyebab: capture jauh kecil
  (~20% lebar) + overexposed (merah pudar jadi pink) → mask S>60 hanya
  dapat setengah papan (aspek 2.2, solidity 0.6).
- Perbaikan `board_utils.py`: ambang merah S 60→40 (stop355 solidity
  0.58→0.99, stop418 aspek 2.19→0.98), stop multi-pass morfologi
  (close 9/5/tanpa) × eps (0.02/0.035), QC global min side 0.08→0.05,
  min area 0.02→0.005 (gerbang poligon/solidity/aspek tetap → sliver aman).
- Jalan 2: 88→33 → jalan 3 (S>40): **2048/2048, 0 reject**.
- False positive tertangkap: `turn_left425` — box 8%x10% di saklar lampu
  tepi frame (papan asli menyatu dinding putih). Guard baru `accept_box()`:
  box area <3% wajib di dekat tengah (|c-0.5|≤0.30). Hasil akhir
  **2047 label**, `turn_left425.jpg` dikecualikan (rugi 1 gambar, aman).
- Sweep tersangka sistematis (area<3% + off-center): hanya 1 file itu.
  Sampling 11/12 label kecil lain benar rapat (green/gray/white wall).

## 3. Distribusi skala (sebelum → sesudah, luas box <15%)
- u_turn 0→158, stop 0→208, turn_left 0→187, turn_right 0→179.
- Total <15%: 0→~732 dari 2047. Data jauh/sedang terisi.

## 4. Sisa Phase 2
- Capture `background/` 50-100 gambar (tanpa rambu) + dukung `.txt` kosong
  di `split_dataset.py` (Phase 3).
- `dataset/` masih split lama → wajib split ulang sebelum retrain (Phase 3+4).
