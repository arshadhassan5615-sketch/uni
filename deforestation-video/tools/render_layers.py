"""Render map layers from downsampled Hansen GFC v1.12 tiles (see hansen_downsample.py).
Outputs (6000x4000 px; mosaic is 12000x8000 cells at ~300 m, written at 6000x4000, equirectangular, lon -70..-40, lat 0..-20):
  base_forest.png         tree cover 2000 (canopy >= 20%), muted green
  loss_YYYY.png (2001-24) forest loss of that year, yellow->red ramp
  borders.svg             Natural Earth country borders + INPE Legal Amazon outline
Usage: python3 -I render_layers.py <ds_dir> <out_dir> <ne_countries.geojson> <legal_amazon.geojson>"""
import sys, json, numpy as np
from PIL import Image
ds, out, ne, la = sys.argv[1:5]
LAYOUT = [["00N_070W", "00N_060W", "00N_050W"], ["10S_070W", "10S_060W", "10S_050W"]]
def mosaic(get):
    return np.vstack([np.hstack([get(t) for t in row]) for row in LAYOUT])
frac = mosaic(lambda t: np.load(f"{ds}/{t}.npz")["frac"])
year = mosaic(lambda t: np.load(f"{ds}/{t}.npz")["year"])
tc = mosaic(lambda t: np.load(f"{ds}/tc_{t}.npy"))
H, W = frac.shape
OUT = (6000, 4000)  # H//2, W//2 of the mosaic
def save(rgb, alpha, name):
    """rgb: 3-tuple constant colour (or HxWx3 array); alpha: HxW float 0..1. 2x2 mean downsample of alpha."""
    a = alpha.reshape(H // 2, 2, W // 2, 2).mean(axis=(1, 3))
    img = np.zeros((H // 2, W // 2, 4), np.uint8)
    img[..., :3] = rgb
    img[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    Image.fromarray(img, "RGBA").save(f"{out}/{name}", optimize=True)
# base forest: tree cover 2000 >= 30% (dataset's standard forest threshold), muted so the loss ramp reads on top
FOREST = tc >= 30
save((0x1D, 0x4D, 0x39), np.where(FOREST, np.clip((tc.astype(np.float32) - 20) / 60, 0.35, 1) * 0.85, 0.0), "base_forest.png")
# loss ramp
stops = np.array([[0xF6, 0xC4, 0x53], [0xF0, 0x8A, 0x3C], [0xD9, 0x48, 0x2B], [0x9E, 0x1B, 0x32]], float)
def ramp(i):  # i in 0..1
    x = i * (len(stops) - 1); k = min(int(x), len(stops) - 2)
    return (stops[k] + (stops[k + 1] - stops[k]) * (x - k)).astype(np.uint8)
for y in range(1, 25):
    m = (year == y) & (frac >= 12) & FOREST   # loss only where the year-2000 cell was forest
    save(tuple(ramp((y - 1) / 23)), np.where(m, np.clip(np.sqrt(frac / 255.0) * 1.25, 0, 1), 0.0), f"loss_{2000 + y}.png")
    print(2000 + y, int(m.sum()), "cells", flush=True)
# borders
LON0, LON1, LAT0, LAT1 = -70, -40, 0, -20
def px(lon, lat): return ((lon - LON0) / (LON1 - LON0) * 6000, (LAT0 - lat) / (LAT0 - LAT1) * 4000)
def rings(geom):
    t = geom["type"]
    polys = geom["coordinates"] if t == "MultiPolygon" else [geom["coordinates"]]
    for p in polys:
        for r in p: yield r
def path(r, step=1):
    pts = r[::step] + [r[-1]]
    return "M" + "L".join("%.1f,%.1f" % px(x, y) for x, y, *_ in pts) + "Z"
parts = []
for f in json.load(open(ne))["features"]:
    for r in rings(f["geometry"]):
        xs = [c[0] for c in r]; ys = [c[1] for c in r]
        if max(xs) < LON0 - 1 or min(xs) > LON1 + 1 or max(ys) < LAT1 - 1 or min(ys) > LAT0 + 1: continue
        parts.append(path(r))
countries = " ".join(parts)
la_parts = [path(r, 6) for f in json.load(open(la))["features"] for r in rings(f["geometry"])]
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 6000 4000" width="6000" height="4000">
<path d="{countries}" fill="none" stroke="#9FB3A6" stroke-opacity="0.55" stroke-width="3" vector-effect="non-scaling-stroke"/>
<path d="{' '.join(la_parts)}" fill="none" stroke="#EAF1EC" stroke-opacity="0.9" stroke-width="4" stroke-dasharray="18 12" vector-effect="non-scaling-stroke"/>
</svg>'''
open(f"{out}/borders.svg", "w").write(svg)
print("done")
