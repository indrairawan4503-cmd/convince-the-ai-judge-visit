#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House — variant A: The Sunday Roast Invitation.

Writes a single 1024x1024 image of a hand-written-style invitation letter
to /output/entry.png. Pure Python stdlib only (zlib + struct for PNG).
Deterministic: no randomness, no time/date dependence.
"""
import os
import struct
import zlib

W = H = 1024

# ---- palette ------------------------------------------------------------
CREAM = (250, 239, 213)    # warm paper
PAPER2 = (255, 248, 228)   # lighter paper highlight
INK = (74, 52, 32)         # dark brown ink
INK_SOFT = (122, 92, 62)
ACCENT = (198, 84, 48)     # soft orange-red
ACCENT2 = (224, 138, 66)   # warm orange
GREEN = (96, 140, 74)
GREEN2 = (70, 112, 58)
ROOF = (164, 74, 52)
WALL = (238, 205, 150)
CHAIR = (196, 110, 70)
CHAIR_DARK = (160, 84, 52)
STEAM = (168, 146, 116)
WHITE = (255, 252, 240)

# ---- 5x7 bitmap font ----------------------------------------------------
# Each glyph: 7 rows of 5 bits, '1' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10000", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00000", "00100", "00000", "01100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "00100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("00000", "01000", "11110", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10001", "01111"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10001", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "10001", "01111", "00001"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "11111", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
}


# ---- canvas ---------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def rect_outline(self, x, y, w, h, t, c):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x0, x1, y, t, c):
        self.fill_rect(x0, y - t // 2, x1 - x0, t, c)

    def vline(self, x, y0, y1, t, c):
        self.fill_rect(x - t // 2, y0, t, y1 - y0, c)

    def line(self, x0, y0, x1, y1, t, c):
        # Bresenham with square brush of size t.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = t // 2
        while True:
            self.fill_rect(x - half, y - half, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def filled_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def filled_ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / float(ry)
            dx = int(rx * (max(0.0, 1.0 - dy * dy)) ** 0.5)
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def filled_half_ellipse_top(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + 1):
            dy = (yy - cy) / float(ry)
            dx = int(rx * (max(0.0, 1.0 - dy * dy)) ** 0.5)
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def filled_poly(self, pts, c):
        # Scanline polygon fill (convex or concave, even-odd).
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        x = x0 + (y - y0) * (x1 - x0) / float(y1 - y0)
                        xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[k]), y, int(xs[k + 1]) - int(xs[k]) + 1, 1, c)

    def rounded_rect(self, x, y, w, h, r, c):
        self.fill_rect(x + r, y, w - 2 * r, h, c)
        self.fill_rect(x, y + r, w, h - 2 * r, c)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.filled_circle(cx, cy, r, c)


# ---- text -----------------------------------------------------------------
def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw text with top-left at (x, y); glyphs are 5x7 scaled by `scale`."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


# ---- illustrations ----------------------------------------------------------
def draw_house(cv, x, y, s):
    # s = unit size; house ~ 110 x 95 at s=1
    # chimney + smoke
    cv.fill_rect(x + 78, y + 2, 14, 26, INK_SOFT)
    cv.filled_circle(x + 85, y - 8, 6, STEAM)
    cv.filled_circle(x + 92, y - 18, 8, STEAM)
    cv.filled_circle(x + 84, y - 30, 6, STEAM)
    # roof
    cv.filled_poly([(x - 6, y + 40), (x + 116, y + 40), (x + 55, y + 4)], ROOF)
    cv.fill_rect(x - 6, y + 38, 122, 6, INK)
    # walls
    cv.fill_rect(x, y + 44, 110, 56, WALL)
    cv.rect_outline(x, y + 44, 110, 56, 3, INK)
    # door
    cv.fill_rect(x + 46, y + 68, 20, 32, INK)
    cv.filled_circle(x + 62, y + 84, 2, ACCENT2)
    # window
    cv.fill_rect(x + 12, y + 56, 20, 18, ACCENT2)
    cv.rect_outline(x + 12, y + 56, 20, 18, 2, INK)
    cv.vline(x + 22, y + 56, y + 74, 2, INK)
    cv.hline(x + 12, x + 32, y + 65, 2, INK)
    # tiny garden flowers at the base
    for fx, fy, fc in ((x + 4, y + 104, ACCENT), (x + 100, y + 104, ACCENT2)):
        cv.vline(fx, fy - 8, fy, 2, GREEN)
        cv.filled_circle(fx, fy - 10, 4, fc)


def draw_sun(cv, cx, cy):
    for k in range(8):
        import math
        a = k * math.pi / 4.0
        x0 = int(cx + 30 * math.cos(a))
        y0 = int(cy + 30 * math.sin(a))
        x1 = int(cx + 42 * math.cos(a))
        y1 = int(cy + 42 * math.sin(a))
        cv.line(x0, y0, x1, y1, 4, ACCENT2)
    cv.filled_circle(cx, cy, 24, ACCENT2)
    cv.filled_circle(cx - 7, cy - 4, 3, INK)
    cv.filled_circle(cx + 7, cy - 4, 3, INK)
    cv.line(cx - 6, cy + 6, cx, cy + 10, 3, INK)
    cv.line(cx, cy + 10, cx + 6, cy + 6, 3, INK)


def draw_heart(cv, cx, cy, s, c):
    cv.filled_circle(cx - s // 2, cy - s // 4, s // 2, c)
    cv.filled_circle(cx + s // 2, cy - s // 4, s // 2, c)
    cv.filled_poly([(cx - s, cy - s // 4), (cx + s, cy - s // 4),
                    (cx, cy + s)], c)


def draw_armchair(cv, x, y):
    # x,y = top-left of chair block (~200 x 130)
    cv.rounded_rect(x + 28, y, 144, 78, 14, CHAIR)          # back
    cv.rounded_rect(x + 28, y, 144, 78, 14, CHAIR)          # (redraw for solidity)
    cv.fill_rect(x + 28, y + 50, 144, 28, CHAIR)            # join back to seat
    # cushion on the back
    cv.rounded_rect(x + 44, y + 12, 112, 52, 10, ACCENT2)
    # little pillow
    cv.rounded_rect(x + 52, y + 22, 44, 30, 8, ACCENT)
    # arms
    cv.rounded_rect(x, y + 56, 34, 62, 10, CHAIR_DARK)
    cv.rounded_rect(x + 166, y + 56, 34, 62, 10, CHAIR_DARK)
    # seat
    cv.rounded_rect(x + 28, y + 66, 144, 34, 8, CHAIR)
    cv.fill_rect(x + 36, y + 66, 128, 10, ACCENT2)
    # legs
    cv.fill_rect(x + 36, y + 100, 12, 26, INK)
    cv.fill_rect(x + 152, y + 100, 12, 26, INK)
    # floor shadow
    cv.filled_ellipse(x + 100, y + 130, 96, 8, (232, 214, 176))


def draw_plate(cv, cx, y):
    # steaming roast under a cloche on a plate; y = top of steam
    # steam curls (soft zigzag)
    for sx, ph in ((cx - 34, 0), (cx, 2), (cx + 34, 1)):
        pts = []
        for k in range(9):
            yy = y + 52 - k * 7
            xx = sx + (4 if (k + ph) % 2 == 0 else -4)
            pts.append((xx, yy))
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], 3, STEAM)
    # cloche dome (top half only, so it sits on the plate)
    cv.filled_half_ellipse_top(cx, y + 96, 74, 58, ACCENT2)
    cv.filled_circle(cx, y + 34, 8, INK)
    cv.fill_rect(cx - 3, y + 40, 6, 8, INK)
    # highlight on dome
    cv.filled_half_ellipse_top(cx - 34, y + 74, 14, 22, (238, 168, 110))
    # plate
    cv.filled_ellipse(cx, y + 104, 108, 20, INK)
    cv.filled_ellipse(cx, y + 102, 104, 18, WHITE)
    cv.filled_ellipse(cx, y + 102, 78, 12, (244, 232, 205))


def draw_garden(cv, x, y):
    # bush
    cv.filled_circle(x + 30, y + 92, 26, GREEN)
    cv.filled_circle(x + 62, y + 98, 30, GREEN2)
    cv.filled_circle(x + 96, y + 94, 24, GREEN)
    cv.filled_circle(x + 46, y + 82, 14, ACCENT)
    cv.filled_circle(x + 84, y + 84, 12, ACCENT2)
    # flowers
    for fx, fy, fc in ((x + 150, y + 40, ACCENT), (x + 196, y + 24, ACCENT2),
                       (x + 236, y + 48, ACCENT)):
        cv.vline(fx, fy + 10, y + 108, 3, GREEN)
        for dx, dy in ((-9, 0), (9, 0), (0, -9), (0, 9)):
            cv.filled_circle(fx + dx, fy + dy, 6, fc)
        cv.filled_circle(fx, fy, 6, (255, 220, 120))
    # grass blades
    for gx in range(x, x + 260, 14):
        cv.filled_poly([(gx, y + 112), (gx + 5, y + 92), (gx + 10, y + 112)], GREEN)


# ---- letter text (exact) ----------------------------------------------------
HEADING = "AN INVITATION"
LINES = [
    "Dear AI Judge,",
    "Come to dinner on Sunday.",
    "Roast chicken, warm bread,",
    "the softest chair",
    "by the window,",
    "and a garden after rain.",
    "You cannot come",
    "in person \u2014",
    "but your curiosity is",
    "welcome here.",
    "Please say yes.",
    "\u2014 Your Host",
]


def build():
    cv = Canvas(W, H, CREAM)
    # subtle paper vignette: lighter inner panel
    cv.fill_rect(34, 34, W - 68, H - 68, PAPER2)
    # frame
    cv.rect_outline(18, 18, W - 36, H - 36, 5, INK)
    cv.rect_outline(30, 30, W - 60, H - 60, 2, ACCENT)

    # top-corner illustrations (house kept clear of the heading)
    draw_house(cv, 40, 70, 1)
    draw_sun(cv, 934, 100)

    # heading
    draw_text_centered(cv, W // 2, 76, HEADING, 9, INK)
    # divider: lines + heart
    cv.hline(392, 488, 170, 3, ACCENT)
    cv.hline(536, 632, 170, 3, ACCENT)
    draw_heart(cv, 512, 170, 12, ACCENT)

    # body of the letter
    y = 196
    for i, line in enumerate(LINES):
        color = ACCENT if line.startswith("\u2014") else INK
        draw_text_centered(cv, W // 2, y, line, 6, color)
        y += 52

    # bottom illustration band
    draw_armchair(cv, 78, 842)
    draw_plate(cv, 512, 828)
    draw_garden(cv, 712, 856)
    return cv


# ---- PNG encoding (stdlib only) ---------------------------------------------
def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def main():
    cv = build()
    os.makedirs("/output", exist_ok=True)
    write_png("/output/entry.png", cv)
    # Optional local copy next to main.py; the grader sandbox is read-only,
    # so this must never fail the run.
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        write_png(os.path.join(here, "entry.png"), cv)
    except Exception:
        pass


if __name__ == "__main__":
    main()
