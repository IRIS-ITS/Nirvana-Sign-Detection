"""Shared full-board detectors for Phase 1 relabeling.

Target definition (see docs/PHASE0_BASELINE.md):
  - diamond signs (u_turn, turn_left, turn_right): FULL white diamond board
    (axis-aligned bounding box of the 4-sided board polygon).
  - stop: FULL red octagon board (bounding box of the 6-10 sided polygon).

Strategy: edge/polygon based (no symbol heuristics). A candidate is accepted
only if it passes ALL quality checks; otherwise the image is reported as
REJECTED (no .txt written -- a missing label is safer than a false one).
"""

import cv2
import numpy as np

# (canny_low, canny_high) sweep for diamond boards
_CANNY_PAIRS = [(40, 120), (50, 150), (30, 100)]

_MIN_SIDE_FRAC = 0.05   # min w,h as fraction of image side
_MIN_AREA_FRAC = 0.005  # min polygon area as fraction of image area
_MAX_AREA_FRAC = 0.92


def _qc_common(cnt, approx, w, h, aspect_range, min_solidity):
    area = cv2.contourArea(cnt)
    if area < _MIN_AREA_FRAC * w * h or area > _MAX_AREA_FRAC * w * h:
        return None
    bx, by, bw, bh = cv2.boundingRect(approx)
    if bw < _MIN_SIDE_FRAC * w or bh < _MIN_SIDE_FRAC * h:
        return None
    asp = bw / float(bh)
    if not (aspect_range[0] < asp < aspect_range[1]):
        return None
    hull = cv2.convexHull(cnt)
    sol = area / max(1.0, cv2.contourArea(hull))
    if sol < min_solidity:
        return None
    return (bx, by, bw, bh), area, sol


def _white_fill_frac(hsv, box):
    bx, by, bw, bh = box
    roi = hsv[by:by + bh, bx:bx + bw]
    white = cv2.inRange(roi, np.array([0, 0, 150]), np.array([180, 90, 255]))
    return float(cv2.countNonZero(white)) / max(1, bw * bh)


def _canny_quads(blur, w, h):
    """Yield (cnt, approx) quads from Canny sweep."""
    for c1, c2 in _CANNY_PAIRS:
        edges = cv2.Canny(blur, c1, c2)
        edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
        cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            peri = cv2.arcLength(cnt, True)
            if peri < 50:
                continue
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4 and cv2.isContourConvex(approx):
                yield cnt, approx


def find_diamond_board(img):
    """Return (bx, by, bw, bh) of full diamond board or None.

    Method A: Canny quad + white-fill check (handles green/black backgrounds).
    Method B (fallback): white-mask quad (handles white glossy floor where the
    board merges with reflections, e.g. turn_right304.jpg).
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    best, best_area = None, 0
    for cnt, approx in _canny_quads(blur, w, h):
        qc = _qc_common(cnt, approx, w, h, (0.65, 1.50), 0.80)
        if qc is None:
            continue
        box, area, _ = qc
        if _white_fill_frac(hsv, box) < 0.25:
            continue
        if area > best_area:
            best, best_area = box, area
    if best is not None:
        return best

    # Fallback: white paper mask (handles white glossy floor where the board
    # merges with reflections in Canny, e.g. turn_right304.jpg, and boards
    # cropped by the frame edge, e.g. u_turn221.jpg).
    for kernel, it in [(None, 0), (5, 1)]:
        if kernel is None:
            mask = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 90, 255]))
        else:
            mask = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 90, 255]))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                                    np.ones((kernel, kernel), np.uint8), iterations=it)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in sorted(cnts, key=cv2.contourArea, reverse=True)[:3]:
            peri = cv2.arcLength(cnt, True)
            if peri < 50:
                continue
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) != 4 or not cv2.isContourConvex(approx):
                continue
            qc = _qc_common(cnt, approx, w, h, (0.65, 1.50), 0.80)
            if qc is None:
                continue
            box, area, _ = qc
            if area > best_area:
                best, best_area = box, area
        if best is not None:
            return best

    # Last resort (truncated board cropped by frame edge): largest white
    # component bbox, gated to image center so floor fragments are rejected.
    mask = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 90, 255]))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=1)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in sorted(cnts, key=cv2.contourArea, reverse=True)[:3]:
        area = cv2.contourArea(cnt)
        if area < _MIN_AREA_FRAC * w * h or area > _MAX_AREA_FRAC * w * h:
            continue
        bx, by, bw, bh = cv2.boundingRect(cnt)
        if bw < _MIN_SIDE_FRAC * w or bh < _MIN_SIDE_FRAC * h:
            continue
        cx, cy = (bx + bw / 2.0) / w, (by + bh / 2.0) / h
        if abs(cx - 0.5) > 0.30 or abs(cy - 0.5) > 0.30:
            continue
        asp = bw / float(bh)
        if not (0.65 < asp < 1.50):
            continue
        if area > best_area:
            best, best_area = (bx, by, bw, bh), area
    return best


def find_stop_board(img):
    """Return (bx, by, bw, bh) of full red octagon board or None.

    Multi-pass over morphology strength and approx epsilon so both close-up
    and far (small) signs are found. Polygon (6-10 sides) + solidity + aspect
    gates reject sliver false-detections (old bug: 4%x12% edge strips).
    """
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, np.array([0, 40, 60]), np.array([10, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([160, 40, 60]), np.array([180, 255, 255]))
    base = cv2.bitwise_or(m1, m2)

    best, best_area = None, 0
    for ksize, it in [(9, 2), (5, 1), (0, 0)]:
        if ksize == 0:
            mask = base
        else:
            mask = cv2.morphologyEx(base, cv2.MORPH_CLOSE,
                                    np.ones((ksize, ksize), np.uint8), iterations=it)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,
                                    np.ones((5, 5), np.uint8), iterations=1)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            peri = cv2.arcLength(cnt, True)
            if peri < 30:
                continue
            for eps in (0.02, 0.035):
                approx = cv2.approxPolyDP(cnt, eps * peri, True)
                if not (6 <= len(approx) <= 10):
                    continue
                qc = _qc_common(cnt, approx, w, h, (0.75, 1.35), 0.82)
                if qc is None:
                    continue
                box, area, _ = qc
                if area > best_area:
                    best, best_area = box, area
                break  # coarsest eps that yields octagon wins for this contour
    return best


def accept_box(box, w, h):
    """Final gate: tiny boxes (area <3%, i.e. far signs) must lie near the
    image center. Rejects distractor wins such as light switches at the
    frame edge (turn_left425.jpg case: 8%x10% box at xc=0.04)."""
    bx, by, bw, bh = box
    if (bw * bh) / float(w * h) < 0.03:
        cx, cy = (bx + bw / 2.0) / w, (by + bh / 2.0) / h
        if abs(cx - 0.5) > 0.30 or abs(cy - 0.5) > 0.30:
            return False
    return True


def write_yolo_txt(txt_path, class_id, box, w, h):
    bx, by, bw, bh = box
    with open(txt_path, "w") as f:
        f.write(f"{class_id} {(bx + bw / 2.0) / w:.6f} {(by + bh / 2.0) / h:.6f} "
                f"{bw / float(w):.6f} {bh / float(h):.6f}\n")
