"""Bake the whole map 'ground' of the film into video/assets/ground.mp4 (1920x1080, 30 fps, full runtime).
It contains: the camera moves over the persistent map, the dimming under each section (scrim), the opening reveal,
the world-to-region push-in, and the 2001-2024 cumulative timelapse. HyperFrames then renders only text/charts/transitions on top.
(Compositing two 6000x4000 layers live in the browser ran at 0.25 fps; the baked ground is a plain video.)
Inputs (made by render_layers.py / bake_maps.py): assets/maps/base_forest.png, loss_YYYY.png; video/assets/maps/loss_all.png.
Usage: python3 -I bake_ground.py <ne_countries.geojson> <legal_amazon.geojson>"""
import sys, json, os, subprocess, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import *

M = f"{ROOT}/assets/maps"; V = f"{ROOT}/video"
BG = (7, 17, 13)
OUT = (1920, 1080)
ne_path, la_path = sys.argv[1], sys.argv[2]
Image.MAX_IMAGE_PIXELS = None

# ---- full-resolution layers (6000x4000)
def solid(): return Image.new("RGBA", (6000, 4000), BG + (255,))
base = Image.open(f"{M}/base_forest.png").convert("RGBA")
bgbase = Image.alpha_composite(solid(), base)

def rings(g):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for p in polys:
        for r in p: yield r
def proj(lon, lat): return ((lon + 70) * 200.0, -lat * 200.0)
def dashed(d, pts, on, off, **kw):
    carry, draw = 0.0, True
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if L == 0: continue
        pos = 0.0
        while pos < L:
            seg = (on if draw else off) - carry; take = min(seg, L - pos)
            if draw: d.line([(x1 + (x2 - x1) * pos / L, y1 + (y2 - y1) * pos / L), (x1 + (x2 - x1) * (pos + take) / L, y1 + (y2 - y1) * (pos + take) / L)], **kw)
            pos += take; carry += take
            if carry >= (on if draw else off): draw, carry = (not draw), 0.0
borders = Image.new("RGBA", (6000, 4000), (0, 0, 0, 0)); bd = ImageDraw.Draw(borders)
for f in json.load(open(ne_path))["features"]:
    for r in rings(f["geometry"]):
        pts = [proj(x, y) for x, y, *_ in r]
        if max(p[0] for p in pts) < -10 or min(p[0] for p in pts) > 6010 or max(p[1] for p in pts) < -10 or min(p[1] for p in pts) > 4010: continue
        bd.line(pts, fill=(159, 179, 166, 150), width=7)
for f in json.load(open(la_path))["features"]:
    for r in rings(f["geometry"]):
        dashed(bd, [proj(a, b) for a, b, *_ in r[::4]], 44, 28, fill=(234, 241, 236, 235), width=10)

loss_all = Image.open(f"{V}/assets/maps/loss_all.png").convert("RGBA")
F0 = solid().convert("RGB")
F1 = bgbase.convert("RGB")
F2 = Image.alpha_composite(bgbase, borders).convert("RGB")
F3 = Image.alpha_composite(Image.alpha_composite(bgbase, loss_all), borders).convert("RGB")   # full world
del loss_all
print("layers ready", flush=True)

# cumulative frames (region window) for the timelapse, built at full resolution so borders match the rest
def crop_win(img, win):
    x0, y0, w = win; h = w * 9 / 16
    return img.resize(OUT, Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h), reducing_gap=3.0)
cum_loss = Image.new("RGBA", (6000, 4000), (0, 0, 0, 0))
cum = [np.asarray(crop_win(F2, W_REGION))]
for y in range(2001, 2025):
    cum_loss = Image.alpha_composite(cum_loss, Image.open(f"{M}/loss_{y}.png").convert("RGBA"))
    flat = Image.alpha_composite(Image.alpha_composite(bgbase, cum_loss), borders).convert("RGB")
    cum.append(np.asarray(crop_win(flat, W_REGION))); del flat
del cum_loss
print("timelapse frames ready", flush=True)

# ---- per-frame rendering
def ease_io(t, p):                     # power(p).inOut
    return 0.5 * (2 * t) ** p if t < 0.5 else 1 - 0.5 * (2 * (1 - t)) ** p
def lerp_win(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def scene_of(t):
    for k in range(1, 11):
        if t < WIN[k][1]: return k
    return 10
def dim(arr, a):
    if a <= 0: return arr
    return (arr.astype(np.float32) * (1 - a) + np.array(BG, np.float32) * a).astype(np.uint8)

total_frames = int(round(TOTAL * FPS)); per = int(round(YEAR_SEC * FPS)); bl = int(round(YEAR_BLEND * FPS))
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "21", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-g", "30", "-movflags", "+faststart", f"{V}/assets/ground.mp4"],
                       stdin=subprocess.PIPE)
for n in range(total_frames):
    t = n / FPS; k = scene_of(t)
    if k == 1:
        t0, t1 = WIN[1]; win = lerp_win(CAM[1][0], CAM[1][1], (t - t0) / (t1 - t0))
        if t < S1_BASE[0]: img = crop_win(F0, win)
        elif t < S1_BASE[1]:
            a = ease_io((t - S1_BASE[0]) / (S1_BASE[1] - S1_BASE[0]), 2); img = Image.blend(crop_win(F0, win), crop_win(F1, win), a)
        elif t < S1_BORDERS[1]:
            a = ease_io(max(0.0, (t - S1_BORDERS[0]) / (S1_BORDERS[1] - S1_BORDERS[0])), 2); img = Image.blend(crop_win(F1, win), crop_win(F2, win), a)
        elif t < S1_LOSS[0]: img = crop_win(F2, win)
        else:
            f = ease_io(min(1.0, (t - S1_LOSS[0]) / (S1_LOSS[1] - S1_LOSS[0])), 3)
            a2, a3 = np.asarray(crop_win(F2, win)), np.asarray(crop_win(F3, win))
            wx = int(round(f * 6000))                                  # world column up to which loss is revealed
            col = np.clip(((win[0] + np.arange(1920) * (win[2] / 1920.0)) < wx), 0, 1)[None, :, None]
            img = np.where(col, a3, a2).astype(np.uint8)
        arr = np.asarray(img) if not isinstance(img, np.ndarray) else img
        arr = dim(arr, SCRIM[1])
    elif k == 6:
        t0, t1 = WIN[6]
        if t < S6_PUSH[0]: win = W_WORLD
        elif t < S6_PUSH[1]: win = lerp_win(W_WORLD, W_REGION, ease_io((t - S6_PUSH[0]) / (S6_PUSH[1] - S6_PUSH[0]), 2))
        else: win = W_REGION
        if t < T6:
            arr = np.asarray(crop_win(F2, win))                       # world without loss during the push
        else:
            i = int((t - T6) * FPS); kk = i // per
            if kk >= 24: arr = cum[24]
            else:
                r = i - kk * per
                if r < bl: a = (r + 1) / (bl + 1); arr = (cum[kk].astype(np.float32) * (1 - a) + cum[kk + 1].astype(np.float32) * a).astype(np.uint8)
                else: arr = cum[kk + 1]
        arr = dim(arr, SCRIM[6])
    else:
        t0, t1 = WIN[k]; win = lerp_win(CAM[k][0], CAM[k][1], (t - t0) / (t1 - t0))
        arr = dim(np.asarray(crop_win(F3, win)), SCRIM[k])
    enc.stdin.write(np.ascontiguousarray(arr).tobytes())
    if n % 600 == 0: print("frame", n, "/", total_frames, flush=True)
enc.stdin.close(); enc.wait(); print("done")
