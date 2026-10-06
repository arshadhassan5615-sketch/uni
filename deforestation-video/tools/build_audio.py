"""Concatenate per-sentence narration into one track with fixed pauses; write video/cues.json (start/end per sentence & section).
Pauses: 1.2 s lead-in, 0.45 s between sentences, 1.5 s between sections, 4.0 s tail. Output loudness-normalised (-16 LUFS, -1.5 dBTP)."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tl = json.load(open(f"{ROOT}/assets/audio/timeline.json"))
LEAD, GAP, SEC_GAP, TAIL = 1.2, 0.45, 1.5, 4.0
t = LEAD; cues = []; sections = {}
prev = None
for c in tl:
    if prev is not None: t += SEC_GAP if c["section"] != prev["section"] else GAP
    c = dict(c); c["start"] = round(t, 3); c["end"] = round(t + c["dur"], 3); t = c["end"]; cues.append(c)
    s = sections.setdefault(c["section"], {"start": c["start"], "end": c["end"]}); s["end"] = c["end"]
    prev = c
total = round(t + TAIL, 3)
inputs, filt = [], []
for i, c in enumerate(cues):
    inputs += ["-i", f"{ROOT}/{c['file']}"]
    ms = int(round(c["start"] * 1000))
    filt.append(f"[{i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=mono,adelay={ms}:all=1[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0:duration=longest,apad=whole_dur={total},atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=7[out]"
os.makedirs(f"{ROOT}/video/assets", exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt) + ";" + mix, "-map", "[out]",
                "-ar", "44100", "-ac", "1", f"{ROOT}/video/assets/narration.wav"], check=True)
json.dump({"total": total, "sections": sections, "cues": cues}, open(f"{ROOT}/video/cues.json", "w"), indent=1, ensure_ascii=False)
print("total", total, "s =", int(total // 60), "min", round(total % 60), "s")
for k, v in sections.items(): print("section", k, v["start"], "->", v["end"], " dur", round(v["end"] - v["start"], 1))
