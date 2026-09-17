import os
from label_u_turn import label_u_turn
from label_stop import label_stop
from label_turn_left import label_turn_left
from label_turn_right import label_turn_right

# Phase 1: full-board auto-labeling (board polygon, not inner symbol).
# Images that fail ALL quality checks are REJECTED (no .txt) -- a missing
# label is safer than a false one. Rejected files are listed for manual review.


def main():
    print("starting auto labeling pipeline (Phase 1: full-board)...")
    total_ok, total_rej = 0, 0
    for fn in (label_u_turn, label_stop, label_turn_left, label_turn_right):
        ok, rej = fn()
        total_ok += ok
        total_rej += len(rej)
    print(f"auto labeling complete. OK={total_ok} REJECTED={total_rej} "
          f"(see per-class lines above; rejected images need manual capture/review)")

if __name__ == "__main__":
    main()
