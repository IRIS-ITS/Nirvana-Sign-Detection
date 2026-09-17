# Phase 1 — Relabel Full-Board (2026-09-18)

## 1. Yang diubah
- **Baru:** `scripts/labeling/board_utils.py` — detektor papan bersama:
  - Diamond (`u_turn/turn_left/turn_right`): Canny sweep quad (4 titik, konveks,
    solidity ≥0.80, white-fill ≥0.25) → fallback white-mask quad (mentah + close
    ringan) → fallback terakhir komponen putih terbesar berpagar tengah
    (untuk papan terpotong tepi frame, mis. `u_turn221.jpg`).
  - Stop: mask merah HSV (H 0-10 & 160-180) + close/open → poligon 6-10 titik
    (oktagon), solidity ≥0.82, aspek 0.75-1.35. Menolak sliver tepi (bug lama).
  - Gagal semua QC → REJECT (tidak tulis `.txt`, dilaporkan).
- **Tulis ulang:** `label_u_turn.py`, `label_stop.py`, `label_turn_left.py`,
  `label_turn_right.py` (wrapper tipis) + `auto_label.py` (ringkasan OK/REJECT).
- **Backup label lama:** `result/label_phase0_backup/`.

## 2. Hasil relabel
- Iterasi 1: OK=1133 REJECT=144 (papan terpotong tepi + 1 jauh+refleksi).
- Setelah fallback white-mask: **OK=1277/1277, REJECT=0**.
- Statistik baru (full papan, wajar besar karena close-up mengisi frame):
  - u_turn: w 0.642 (0.412-0.738), h 0.849 (0.537-0.960)
  - stop: w 0.605 (0.348-0.703), h 0.782 (0.469-0.935)
  - turn_left: w 0.626 (0.417-0.764), h 0.822 (0.550-1.000)
  - turn_right: w 0.624 (0.431-0.711), h 0.812 (0.554-0.942)
- Perbaikan kunci: `stop144` sliver `4%x12%` → oktagon `52%x77%`;
  `turn_right304` jauh+refleksi → `43%x56%` tepat; sampel terpotong tepi
  (`u221`, `tl54`, `tr250`) terbungkus rapat.

## 3. Bukti visual
- `docs/previews_phase1/grid_{u_turn,stop,turn_left,turn_right}_*.jpg`
  (24/23 sampel per kelas, semua rapat full-papan termasuk sampel jauh kecil).
- `/tmp/opencode/phase1_fixed_check.jpg` (6 sampel paling sulit, before concern → now OK).

## 4. Catatan penting
- Box GT kini BESAR (mean ~62%x82%) karena definisi full-papan + data close-up.
  Ini benar secara semantik; efek "memenuhi layar" saat live-dekat hanya hilang
  setelah **retrain (Phase 4)** + data jarak jauh + fix letterbox (`detect.cpp`).
- `dataset/` masih berisi label LAMA — wajib `split_dataset.py` ulang (Phase 3)
  sebelum retrain. Model `best.onnx` saat ini masih terlatih label lama.
- Sisa risiko: data masih monoton (tengah, dekat, tanpa background negatif).
  Ditangani Phase 2 (tambah capture jauh + background) / augmentasi skala saat training.
