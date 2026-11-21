#!/usr/bin/env python3
"""Passport of Nowhere - draws an invented passport spread as entry.png.
Pure Python 3 stdlib, deterministic, no network, no external files.
Canvas + bitmap font + zlib PNG encoder written for this entry.
"""
import os, struct, zlib, math

W, H = 1024, 768

# ---------- tiny 5x7 bitmap font (rows top->bottom, 5 bits) ----------
F = {
 'A':(0x0E,0x11,0x11,0x1F,0x11,0x11,0x11),'B':(0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E),
 'C':(0x0E,0x11,0x10,0x10,0x10,0x11,0x0E),'D':(0x1C,0x12,0x11,0x11,0x11,0x12,0x1C),
 'E':(0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F),'F':(0x1F,0x10,0x10,0x1E,0x10,0x10,0x10),
 'G':(0x0E,0x11,0x10,0x17,0x11,0x11,0x0F),'H':(0x11,0x11,0x11,0x1F,0x11,0x11,0x11),
 'I':(0x0E,0x04,0x04,0x04,0x04,0x04,0x0E),'J':(0x07,0x02,0x02,0x02,0x02,0x12,0x0C),
 'K':(0x11,0x12,0x14,0x18,0x14,0x12,0x11),'L':(0x10,0x10,0x10,0x10,0x10,0x10,0x1F),
 'M':(0x11,0x1B,0x15,0x15,0x11,0x11,0x11),'N':(0x11,0x19,0x15,0x13,0x11,0x11,0x11),
 'O':(0x0E,0x11,0x11,0x11,0x11,0x11,0x0E),'P':(0x1E,0x11,0x11,0x1E,0x10,0x10,0x10),
 'Q':(0x0E,0x11,0x11,0x11,0x15,0x12,0x0D),'R':(0x1E,0x11,0x11,0x1E,0x14,0x12,0x11),
 'S':(0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E),'T':(0x1F,0x04,0x04,0x04,0x04,0x04,0x04),
 'U':(0x11,0x11,0x11,0x11,0x11,0x11,0x0E),'V':(0x11,0x11,0x11,0x11,0x11,0x0A,0x04),
 'W':(0x11,0x11,0x11,0x15,0x15,0x1B,0x11),'X':(0x11,0x0A,0x04,0x04,0x04,0x0A,0x11),
 'Y':(0x11,0x0A,0x04,0x04,0x04,0x04,0x04),'Z':(0x1F,0x01,0x02,0x04,0x08,0x10,0x1F),
 '0':(0x0E,0x11,0x13,0x15,0x19,0x11,0x0E),'1':(0x04,0x0C,0x04,0x04,0x04,0x04,0x0E),
 '2':(0x0E,0x11,0x01,0x02,0x04,0x08,0x1F),'3':(0x1E,0x01,0x02,0x0C,0x01,0x11,0x0E),
 '4':(0x02,0x06,0x0A,0x12,0x1F,0x02,0x02),'5':(0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E),
 '6':(0x06,0x08,0x10,0x1E,0x11,0x11,0x0E),'7':(0x1F,0x01,0x02,0x04,0x08,0x08,0x08),
 '8':(0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E),'9':(0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C),
 ' ':(0,0,0,0,0,0,0),'.':(0,0,0,0,0,0x0C,0x0C),',':(0,0,0,0,0,0x0C,0x04),
 '-':(0,0,0,0x1F,0,0,0),'/':(0x01,0x01,0x02,0x04,0x08,0x10,0x10),
 ':':(0,0,0x0C,0,0,0x0C,0),'<':(0x02,0x04,0x08,0x10,0x08,0x04,0x02),
 "'":(0x04,0x04,0x08,0,0,0,0),'(':(0x02,0x04,0x08,0x08,0x08,0x04,0x02),
 ')':(0x08,0x04,0x02,0x02,0x02,0x04,0x08),'&':(0x0C,0x12,0x14,0x08,0x15,0x12,0x0D),
 '+':(0,0x04,0x04,0x1F,0x04,0x04,0),'*':(0,0x15,0x0E,0x15,0,0,0),
}

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))
    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i+3] = bytes(c)
    def blend(self, x, y, c, a):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            for k in range(3):
                self.px[i+k] = int(self.px[i+k] * (1 - a) + c[k] * a)
    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.set(x, y, c)
    def frame(self, x0, y0, x1, y1, c, t=2):
        self.rect(x0, y0, x1, y0 + t, c); self.rect(x0, y1 - t, x1, y1, c)
        self.rect(x0, y0, x0 + t, y1, c); self.rect(x1 - t, y0, x1, y1, c)
    def line(self, x0, y0, x1, y1, c, t=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i // n; y = y0 + (y1 - y0) * i // n
            for dy in range(t):
                for dx in range(t):
                    self.set(x + dx, y + dy, c)
    def circle(self, cx, cy, r, c, fill=False, t=2):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d2 = dx * dx + dy * dy
                if fill and d2 <= r * r:
                    self.set(cx + dx, cy + dy, c)
                elif not fill and (r - t) * (r - t) <= d2 <= r * r:
                    self.set(cx + dx, cy + dy, c)
    def ellipse_frame(self, cx, cy, rx, ry, c, t=2):
        for a in range(720):
            th = a * math.pi / 360.0
            for k in range(t):
                self.set(int(cx + (rx - k) * math.cos(th)),
                         int(cy + (ry - k) * math.sin(th)), c)
    def text(self, x, y, s, c, sc=2, sp=None):
        sp = sp if sp is not None else sc
        cx = x
        for ch in s.upper():
            g = F.get(ch, F[' '])
            for r in range(7):
                bits = g[r]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * sc, y + r * sc,
                                  cx + (col + 1) * sc, y + (r + 1) * sc, c)
            cx += (5 * sc + sp)
        return cx - sp
    def text_c(self, cx, y, s, c, sc=2, sp=None):
        sp = sp if sp is not None else sc
        wdt = len(s) * (5 * sc + sp) - sp
        return self.text(cx - wdt // 2, y, s, c, sc, sp)
    def text_r(self, xr, y, s, c, sc=2, sp=None):
        sp = sp if sp is not None else sc
        wdt = len(s) * (5 * sc + sp) - sp
        return self.text(xr - wdt, y, s, c, sc, sp)

def save_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# ---------- palette ----------
NAVY = (27, 42, 92); GOLD = (176, 141, 62); PAPER = (243, 238, 222)
PAPER2 = (236, 229, 205); INK = (32, 34, 38); GREY = (96, 98, 102)
FAINT = (168, 160, 132); RED = (168, 42, 48); BLUE = (36, 74, 148)
TEAL = (24, 110, 108); DARK = (18, 20, 24)

def guilloche(cv, x0, y0, x1, y1, c, step=9):
    # fine wavy security lines across a page area
    for yy in range(y0, y1, step):
        for xx in range(x0, x1):
            off = int(3 * math.sin((xx - x0) / 34.0 + yy / 22.0))
            cv.blend(xx, yy + off, c, 0.35)
    for xx in range(x0, x1, step * 2):
        for yy in range(y0, y1):
            off = int(3 * math.cos((yy - y0) / 30.0 + xx / 26.0))
            cv.blend(xx + off, yy, c, 0.22)

def emblem(cv, cx, cy):
    # coat of arms: shield, lighthouse, waves, star - the maritime republic
    cv.circle(cx, cy - 34, 13, GOLD, fill=True)
    for dx, dy in ((-26, -44), (26, -44), (0, -52)):
        cv.line(cx, cy - 34, cx + dx, cy - 34 + dy, GOLD, 2)
    for yy in range(cy - 30, cy + 34):
        wdt = 30 - abs(yy - cy) // 6
        cv.rect(cx - wdt, yy, cx + wdt, yy + 1, NAVY)
    cv.frame(cx - 32, cy - 32, cx + 32, cy + 36, GOLD, 2)
    cv.rect(cx - 6, cy - 22, cx + 6, cy + 8, PAPER)      # lighthouse tower
    cv.rect(cx - 11, cy - 28, cx + 11, cy - 20, RED)     # lamp room
    for k in range(3):  # waves
        for xx in range(cx - 24, cx + 24):
            yy = cy + 14 + k * 7 + int(2 * math.sin(xx / 6.0 + k))
            cv.set(xx, yy, (140, 190, 220)); cv.set(xx, yy + 1, (140, 190, 220))
    cv.text_c(cx, cy + 44, "AURALIS", GOLD, 2)

def portrait(cv, x0, y0, x1, y1):
    # dignified drawn portrait: Auralian holder, harbour light behind
    cv.rect(x0, y0, x1, y1, (196, 205, 214))
    for i in range(24):  # photo backdrop bands (harbour sky)
        cv.rect(x0, y0 + i * 6, x1, y0 + i * 6 + 3, (176, 192, 208))
    cv.rect(x0, y1 - 34, x1, y1, (120, 148, 168))  # sea band
    cx, cy = (x0 + x1) // 2, y0 + 62
    for dy in range(-46, 47):  # head
        hw = int(34 * math.sqrt(max(0, 1 - (dy / 46.0) ** 2)))
        cv.rect(cx - hw, cy + dy, cx + hw, cy + dy + 1, (206, 168, 138))
    cv.rect(cx - 30, cy - 48, cx + 30, cy - 22, (52, 44, 40))  # hair
    cv.rect(cx - 34, cy - 30, cx - 26, cy + 6, (52, 44, 40))
    cv.rect(cx + 26, cy - 30, cx + 34, cy + 6, (52, 44, 40))
    for ex in (cx - 14, cx + 14):  # eyes
        cv.rect(ex - 4, cy - 2, ex + 4, cy + 2, DARK)
    cv.rect(cx - 2, cy + 2, cx + 1, cy + 14, (178, 138, 108))  # nose
    cv.rect(cx - 9, cy + 22, cx + 9, cy + 25, (150, 84, 80))   # mouth
    cv.rect(cx - 52, y1 - 62, cx + 52, y1, (44, 52, 76))       # shoulders/coat
    cv.rect(cx - 10, y1 - 62, cx + 10, y1 - 30, PAPER)         # shirt
    cv.rect(cx - 4, y1 - 58, cx + 4, y1 - 28, RED)             # tie
    cv.frame(x0, y0, x1, y1, GREY, 2)
    cv.text_c(cx, y1 - 16, "VEY M S", (240, 240, 240), 1)

def field(cv, x, y, label, value, sc=2):
    cv.text(x, y, label, GREY, 1)
    cv.text(x, y + 10, value, INK, sc)
    cv.line(x, y + 10 + 7 * sc + 5, x + 228, y + 10 + 7 * sc + 5, FAINT, 1)

def stamp_round(cv, cx, cy, r, col, lines, rot=0.0):
    cv.circle(cx, cy, r, col, t=3); cv.circle(cx, cy, r - 7, col, t=2)
    n = len(lines)
    for i, s in enumerate(lines):
        yy = cy - (n * 16) // 2 + i * 16
        # slight rotation faked by per-line x offset
        cv.text_c(cx + int(rot * (yy - cy)), yy, s, col,
                  1 if len(s) > 12 else 2, sp=0)

def stamp_rect(cv, x0, y0, col, lines, angle_off=0):
    wdt = max(len(s) for s in lines) * 12 + 22
    hgt = len(lines) * 18 + 16
    cv.frame(x0, y0, x0 + wdt, y0 + hgt, col, 3)
    for i, s in enumerate(lines):
        cv.text(x0 + 11 + (angle_off if i % 2 else 0), y0 + 9 + i * 18, s, col,
                1 if len(s) > 14 else 2)
    return x0 + wdt, y0 + hgt

def draw():
    cv = Canvas(W, H, NAVY)
    cv.rect(10, 10, W - 10, H - 10, PAPER)
    cv.rect(10, 10, W - 10, 26, NAVY); cv.rect(10, H - 26, W - 10, H - 10, NAVY)
    cv.rect(506, 10, 518, H - 10, (206, 196, 164))  # centre gutter
    guilloche(cv, 26, 34, 500, 560, (150, 168, 150))
    guilloche(cv, 524, 34, 998, 560, (150, 168, 150))
    # ---------- LEFT PAGE: data page ----------
    cv.text_c(263, 40, "REPUBLIC OF AURALIS", NAVY, 3)
    cv.text_c(263, 66, "REPUBLIQUE D AURALIS  -  PASSPORT", GOLD, 1)
    cv.line(36, 84, 490, 84, GOLD, 2)
    emblem(cv, 92, 140)
    cv.text(150, 100, "PASSEPORT", NAVY, 2)
    cv.text(150, 122, "PASSPORT  AUR", NAVY, 2)
    cv.text(150, 146, "NO  AUR 0482716", RED, 2)
    cv.text(150, 170, "CODE  AUR", GREY, 1)
    portrait(cv, 36, 216, 196, 420)
    fx = 214
    field(cv, fx, 210, "SURNAME / NOM", "VEY")
    field(cv, fx, 258, "GIVEN NAMES / PRENOMS", "MIRA SOLENNE")
    field(cv, fx, 306, "NATIONALITY / NATIONALITE", "AURALIAN")
    field(cv, fx, 354, "DATE OF BIRTH / NE LE", "22 JUN 1994")
    field(cv, fx, 402, "PLACE OF BIRTH / LIEU", "PORT LUMEN")
    field(cv, fx, 450, "SEX / SEXE   HEIGHT", "F    168 CM")
    cv.text(36, 486, "ISSUED / DELIVRE  PORT LUMEN", INK, 1)
    cv.text(36, 504, "14 MAR 2021", INK, 2)
    cv.text(268, 486, "EXPIRES / EXPIRE", INK, 1)
    cv.text(268, 504, "14 MAR 2031", INK, 2)
    cv.text(36, 534, "AUTHORITY  MINISTRY OF TIDES AND HARBOURS", GREY, 1)
    # machine-readable zone
    cv.rect(26, 566, 500, 742, (226, 220, 198))
    cv.line(26, 566, 500, 566, NAVY, 2)
    mrz1 = "P<AURVEY<<MIRA<SOLENNE<<<<<<<<<<<<<<<<<<<<"
    mrz2 = "AUR0482716<4AUR9406228F3103142<<<<<<<<<<06"
    cv.text(40, 596, mrz1[:43], INK, 2, sp=0)
    cv.text(40, 636, mrz2[:43], INK, 2, sp=0)
    cv.text(40, 682, "HOLDER MUST CARRY TIDE TABLE - SEE PAGE 3", TEAL, 1)
    cv.text(40, 702, "SIGNATURE  M. S. VEY", INK, 1)
    # ---------- RIGHT PAGE: visas & stamps ----------
    cv.text_c(761, 40, "VISAS", NAVY, 3)
    cv.text_c(761, 66, "ENDORSEMENTS  -  OBSERVATIONS", GOLD, 1)
    cv.line(532, 84, 990, 84, GOLD, 2)
    cv.text(532, 96, "CONDITION OF STAY (TIDE LAW, ART. 7)", TEAL, 1)
    cv.text(532, 112, "HOLDER MUST REGISTER TIDE TABLE AT", INK, 1)
    cv.text(532, 128, "EACH PORT OF CALL. HARBOUR DUES PAID", INK, 1)
    cv.text(532, 144, "IN AURALIAN LITRES. SEE FEE STAMP.", INK, 1)
    # fee stamp - the telling detail
    stamp_rect(cv, 800, 96, TEAL, ["TIDE FEE", "PAID 12 L"], 0)
    # travel history: all after issue 14 MAR 2021, chronological
    stamp_round(cv, 622, 252, 72, BLUE,
                ["VELMARRA", "ARRIVED", "03 JUL 2022"], 0.06)
    stamp_round(cv, 884, 252, 72, RED,
                ["VELMARRA", "DEPARTED", "18 JUL 2022"], -0.05)
    stamp_rect(cv, 540, 348, BLUE,
               ["OSTRAVIA - KEST PORT", "ENTRY 09 MAY 2023"], 2)
    stamp_rect(cv, 736, 424, RED,
               ["OSTRAVIA - KEST PORT", "EXIT  27 MAY 2023"], -2)
    stamp_round(cv, 640, 512, 62, TEAL,
                ["KESTREL IS.", "ARRIVED", "02 NOV 2024"], -0.04)
    # language column + microtext rows
    cv.text(532, 596, "AURALIC", INK, 1)
    cv.text(532, 614, "THIS PASSPORT IS VALID FOR ALL", GREY, 1)
    cv.text(532, 632, "COUNTRIES. 48 PAGES. NO. AUR0482716", GREY, 1)
    cv.text(760, 596, "ENGLISH", INK, 1)
    cv.text(760, 614, "EN CAS D URGENCE AVISER LE", GREY, 1)
    cv.text(760, 632, "CONSULAT D AURALIS A PORT LUMEN", GREY, 1)
    for i in range(4):
        yy = 668 + i * 16
        cv.text(532, yy, "REPUBLICOFAURALIS*MINISTRYOFTIDES*" * 2, FAINT, 1)
    cv.text_c(761, 724, "PAGE 2  -  AUR 0482716  -  PORT LUMEN", GREY, 1)
    return cv

def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    save_png(draw(), os.path.join(out, "entry.png"))

if __name__ == "__main__":
    main()

