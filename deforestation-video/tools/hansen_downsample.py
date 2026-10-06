"""Downsample a Hansen GFC 10x10 degree tile into block statistics.
Per output cell (FACTOR x FACTOR source pixels, ~30 m each):
  frac  = share of source pixels with loss (uint8 0..255)
  year  = mean loss year of those pixels (1..24 -> 2001..2024), 0 if none
Usage: python3 -I hansen_downsample.py <lossyear.tif> <out.npz> [factor]
"""
import sys, numpy as np, rasterio
src, out = sys.argv[1], sys.argv[2]
F = int(sys.argv[3]) if len(sys.argv) > 3 else 10
STRIP = 2000  # source rows per read, divisible by F
with rasterio.open(src) as d:
    H, W = d.height, d.width
    oh, ow = H // F, W // F
    frac = np.zeros((oh, ow), np.uint8)
    year = np.zeros((oh, ow), np.uint8)
    for r0 in range(0, H, STRIP):
        a = d.read(1, window=((r0, r0 + STRIP), (0, W)))
        n = STRIP // F
        b = a.reshape(n, F, ow, F).transpose(0, 2, 1, 3).reshape(n, ow, F * F)
        m = b > 0
        cnt = m.sum(2)
        s = (b.astype(np.uint32) * m).sum(2)
        o = r0 // F
        frac[o:o + n] = np.round(255 * cnt / (F * F)).astype(np.uint8)
        year[o:o + n] = np.where(cnt > 0, np.round(s / np.maximum(cnt, 1)), 0).astype(np.uint8)
    np.savez_compressed(out, frac=frac, year=year, bounds=np.array(d.bounds), factor=F)
print(out, frac.shape, int((frac > 0).sum()), "cells with loss")
