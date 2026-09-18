# Auto-Labeling Rambu (`scripts/labeling/`)

name : Brenanda Caesa Pamudya
email : brenandapamudya178@gmail.com

Membuat anotasi bounding box `.txt` format YOLO secara otomatis dari `result/raw/<kelas>/` ke `result/label/<kelas>/`.

## Definisi Target Box

**Full papan rambu**, bukan simbol di dalamnya:

| Kelas | Target |
|---|---|
| `u_turn` (0) | Wajik putih penuh |
| `stop` (1) | Oktagon merah penuh |
| `turn_left` (2) | Wajik putih penuh |
| `turn_right` (3) | Wajik putih penuh |

## Isi Modul

- **board_utils.py** — Detektor papan bersama:
  - Wajik: Canny sweep quad (4 titik, konveks, solidity ≥0.80, white-fill ≥0.25) → fallback white-mask quad (mentah + close ringan) → fallback komponen putih terbesar berpagar tengah (papan terpotong tepi frame).
  - STOP: mask merah HSV (S>40 agar tahan overexposure) multi-pass morfologi × aproksimasi (poligon 6-10 sisi, solidity ≥0.82, aspek 0.75-1.35).
  - `accept_box()`: guard tiny-box — box luas <3% wajib di dekat tengah frame (menolak distraktor tepi seperti saklar lampu).
- **label_u_turn.py / label_stop.py / label_turn_left.py / label_turn_right.py** — Wrapper tipis per kelas (bisa dijalankan tunggal).
- **auto_label.py** — Menjalankan keempatnya + ringkasan OK/REJECT.
- **visualize_labels.py** — Preview 1 sampel visualisasi per kelas ke `docs/previews/`.

## Kebijakan REJECT

Gambar yang gagal **semua** QC tidak ditulis `.txt`-nya dan dilaporkan di console. Label yang hilang lebih aman daripada label palsu — `split_dataset.py` otomatis melewati gambar tanpa pasangan valid. Contoh kasus nyata yang pernah tertangkap: strip tepi palsu pada STOP, dan box saklar lampu (`turn_left425`).

## Background

Kelas `background/` **tidak** lewat modul ini: `.txt` kosong dibuat otomatis oleh `take_background` saat capture.

## Cara Pakai

```bash
# Dari root repository
nirvana.venv/bin/python scripts/labeling/auto_label.py
```

Contoh output:

```text
u_turn: processed 513/513 full-board labels into result/label/u_turn
stop: processed 531/531 full-board labels into result/label/stop
...
auto labeling complete. OK=2047 REJECTED=1
```

Setelah ini, verifikasi visual (lihat grid preview) lalu lanjut `scripts/split_dataset.py`.
