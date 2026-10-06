"""Generate narration, one audio clip per sentence, with Fish Audio (voice 2947ec32..., model s2.1-pro-free).
Reads SCRIPT.md (lines starting with '>'), writes assets/audio/s<section>_<n>.wav and assets/audio/timeline.json.
Key is read from the FISH_API_KEY environment variable only. Clips are cached by text hash."""
import os, re, sys, json, time, hashlib, subprocess, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio"); os.makedirs(OUT, exist_ok=True)
KEY = os.environ["FISH_API_KEY"]
VOICE = "2947ec32c7e1479c8ec5628a1fc035f1"
PRON = [("INPE", "I N P E"), ("PRODES", "Prodes"), ("FAO", "F A O"), ("Sentinel-2", "Sentinel two"),
        ("U S ", "U S "), ("km²", "square kilometres")]
sections, cur = [], None
for line in open(os.path.join(ROOT, "SCRIPT.md"), encoding="utf-8"):
    m = re.match(r"## (\d+)\. ", line)
    if m: cur = {"id": int(m.group(1)), "sentences": []}; sections.append(cur); continue
    if line.startswith(">") and cur is not None:
        txt = re.sub(r"\[[\d\]\[, ]+\]", "", line[1:]).strip()
        for s in re.split(r"(?<=[.?!])\s+", txt):
            if s.strip(): cur["sentences"].append(s.strip())
def say(text, path):
    spoken = text
    for a, b in PRON: spoken = spoken.replace(a, b)
    body = json.dumps({"text": spoken, "reference_id": VOICE, "format": "wav", "temperature": 0.5,
                       "prosody": {"speed": 0.95, "normalize_loudness": True}}).encode()
    for attempt in range(5):
        req = urllib.request.Request("https://api.fish.audio/v1/tts", data=body, method="POST",
              headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "model": "s2.1-pro-free"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r: open(path, "wb").write(r.read()); return
        except Exception as e:
            print("  retry", attempt, e, file=sys.stderr); time.sleep(3 * (attempt + 1))
    raise SystemExit("FAILED: " + text)
def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
tl = []
for sec in sections:
    for i, s in enumerate(sec["sentences"]):
        h = hashlib.sha1((s + VOICE).encode()).hexdigest()[:8]
        p = os.path.join(OUT, f"s{sec['id']:02d}_{i+1:02d}_{h}.wav")
        if not os.path.exists(p): say(s, p); print("made", os.path.basename(p), flush=True)
        tl.append({"section": sec["id"], "n": i + 1, "text": s, "file": os.path.relpath(p, ROOT), "dur": round(dur(p), 3)})
json.dump(tl, open(os.path.join(OUT, "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(tl), "clips, total speech", round(sum(c["dur"] for c in tl), 1), "s")
