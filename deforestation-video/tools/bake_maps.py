"""Bake map assets for the video from assets/maps layers.
 1. video/assets/maps/loss_all.png : all years 2001-2024 composited (6000x4000, transparent)
 2. video/assets/amazon_timelapse.mp4 : cumulative loss 2001->2024 in the REGION window (world px x800..4400, y600..2625)
    1920x1080, 30 fps, YEAR_SEC per year (+0.25 s blend), then holds the final frame until DURATION.
Usage: python3 -I bake_maps.py <ne_countries.geojson> <legal_amazon.geojson> <timelapse_total_seconds>"""
import sys, json, subprocess, numpy as np, os
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ne, la, DURATION = sys.argv[1], sys.argv[2], float(sys.argv[3])
M = f"{ROOT}/assets/maps"; V = f"{ROOT}/video"
YEAR_SEC, BLEND, FPS = 0.8, 0.25, 30
X0, Y0, WW, HH = 800, 600, 3600, 2025      # REGION window in 6000x4000 world px
OUT = (1920, 1080); S = OUT[0] / WW
# 1. composite all years (full res)
acc = Image.new("RGBA", (6000, 4000), (0, 0, 0, 0))
for y in range(2001, 2025): acc = Image.alpha_composite(acc, Image.open(f"{M}/loss_{y}.png"))
acc.save(f"{V}/assets/maps/loss_all.png", optimize=True); del acc
# 2. cumulative frames in region window
bg = Image.new("RGBA", OUT, (7, 17, 13, 255))
base = Image.open(f"{M}/base_forest.png").crop((X0, Y0, X0 + WW, Y0 + HH)).resize(OUT, Image.LANCZOS)
bg = Image.alpha_composite(bg, base)
def project(lon, lat): return ((((lon + 70) * 200) - X0) * S, ((-lat * 200) - Y0) * S)
ov = Image.new("RGBA", (OUT[0] * 2, OUT[1] * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
def rings(g):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for p in polys:
        for r in p: yield r
for f in json.load(open(ne))["features"]:
    for r in rings(f["geometry"]):
        pts = [project(x, y) for x, y, *_ in r]
        if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > OUT[0] + 50 or max(p[1] for p in pts) < -50 or min(p[1] for p in pts) > OUT[1] + 50: continue
        d.line([(x * 2, y * 2) for x, y in pts], fill=(159, 179, 166, 140), width=3)
def dashed(pts, on=22, off=14, **kw):
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
for f in json.load(open(la))["features"]:
    for r in rings(f["geometry"]):
        pts = [(x * 2, y * 2) for x, y in (project(a, b) for a, b, *_ in r[::4])]
        dashed(pts, fill=(234, 241, 236, 235), width=5)
ov = ov.resize(OUT, Image.LANCZOS)
cum = []; cur = Image.new("RGBA", OUT, (0, 0, 0, 0))
for y in range(2001, 2025):
    lay = Image.open(f"{M}/loss_{y}.png").crop((X0, Y0, X0 + WW, Y0 + HH)).resize(OUT, Image.LANCZOS)
    cur = Image.alpha_composite(cur, lay)
    cum.append(np.asarray(Image.alpha_composite(Image.alpha_composite(bg, cur), ov).convert("RGB")))
first = np.asarray(Image.alpha_composite(bg, ov).convert("RGB"))
cum = [first] + cum   # index 0 = no loss yet, then through 2001..2024
total_frames = int(round(DURATION * FPS)); per = int(round(YEAR_SEC * FPS)); bl = int(round(BLEND * FPS))
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", f"{V}/assets/amazon_timelapse.mp4"], stdin=subprocess.PIPE)
for n in range(total_frames):
    k = n // per                       # which year step we're in (0..)
    if k >= 24: img = cum[24]
    else:
        r = n - k * per                # frame within this year step; blend from cum[k] -> cum[k+1] in the first `bl` frames
        if r < bl:
            a = (r + 1) / (bl + 1); img = (cum[k].astype(np.float32) * (1 - a) + cum[k + 1].astype(np.float32) * a).astype(np.uint8)
        else: img = cum[k + 1]
    p.stdin.write(np.ascontiguousarray(img).tobytes())
p.stdin.close(); p.wait(); print("frames", total_frames)
