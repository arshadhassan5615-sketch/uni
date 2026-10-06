"""Mean canopy cover (0-100) per FACTOR x FACTOR block of a Hansen treecover2000 tile.
Usage: python3 -I treecover_downsample.py <treecover2000.tif> <out.npy> [factor]"""
import sys, numpy as np, rasterio
src, out = sys.argv[1], sys.argv[2]
F = int(sys.argv[3]) if len(sys.argv) > 3 else 10
STRIP = 2000
with rasterio.open(src) as d:
    H, W = d.height, d.width
    res = np.zeros((H // F, W // F), np.uint8)
    for r0 in range(0, H, STRIP):
        a = d.read(1, window=((r0, r0 + STRIP), (0, W))).astype(np.uint16)
        n = STRIP // F
        res[r0 // F:r0 // F + n] = a.reshape(n, F, W // F, F).mean(axis=(1, 3)).round().astype(np.uint8)
np.save(out, res); print(out, res.shape, int(res.max()))
