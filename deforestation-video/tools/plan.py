"""Shared timing plan for the HTML composition (build_video.py) and the baked ground video (bake_ground.py).
Everything is derived from video/cues.json (sentence start/end times of the narration)."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f"{ROOT}/video/cues.json"))
TOTAL = D["total"]
FPS = 30
CUE = {(c["section"], c["n"]): c for c in D["cues"]}
SEC = {int(k): v for k, v in D["sections"].items()}
st = lambda s, n: CUE[(s, n)]["start"]
en = lambda s, n: CUE[(s, n)]["end"]
MID = {k: round((SEC[k]["end"] + SEC[k + 1]["start"]) / 2, 3) for k in range(1, 10)}   # curtain centre between sections
WIN = {k: (0.0 if k == 1 else MID[k - 1], TOTAL if k == 10 else MID[k]) for k in range(1, 11)}

# camera windows in 6000x4000 world px: (x0, y0, width); height = width * 9/16. 200 world px per degree; lon -70..-40, lat 0..-20
W_WORLD, W_REGION = (0, 200, 6000), (800, 600, 3600)
CAM = {1: ((0, 200, 6000), (120, 260, 5760)), 2: ((800, 600, 3600), (900, 640, 3400)), 3: ((2300, 900, 3600), (2200, 960, 3400)),
       4: ((300, 500, 3600), (400, 540, 3400)), 5: ((1400, 1100, 3600), (1500, 1060, 3400)),
       7: (W_REGION, (840, 620, 3520)), 8: ((2000, 500, 3600), (2100, 540, 3400)), 9: (W_WORLD, (60, 230, 5880)), 10: ((600, 400, 4000), (640, 420, 3900))}
SCRIM = {1: 0.0, 2: 0.80, 3: 0.88, 4: 0.88, 5: 0.86, 6: 0.0, 7: 0.62, 8: 0.90, 9: 0.0, 10: 0.94}   # dimming of the map under each section

# S1 reveal (seconds): ground fades in, borders fade in, loss wipes in left to right
S1_BASE = (0.6, 3.4); S1_BORDERS = (3.4, 5.0); S1_LOSS = (st(1, 2), st(1, 2) + 4.0)
# S6: push-in from world to region, then the 2001-2024 cumulative timelapse starts at T6
S6_PUSH = (st(6, 1) + 0.1, st(6, 1) + 3.8)
T6 = st(6, 1) + 3.9
YEAR_SEC, YEAR_BLEND = 0.8, 0.25
