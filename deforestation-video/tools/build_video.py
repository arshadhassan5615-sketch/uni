"""Generate video/index.html (HyperFrames composition) from video/cues.json.
Edit THIS file, never the generated HTML. Run: python3 -I tools/build_video.py

World model (video-storytelling): one persistent map ground (baked into assets/ground.mp4 by bake_ground.py, camera moves included); each section is a
clip of overlays. Sections are separated by a dark curtain wipe that sits in the silent gap between
sentences; scene content is never animated out before its curtain (HyperFrames transition rule).
Every factual on-screen string is traceable to FACT-SHEET.md (row numbers in comments)."""
import json, os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import *

CUR_IN, CUR_HOLD, CUR_OUT = 0.45, 0.20, 0.45   # curtain timing around each MID

js = []
def J(s): js.append(s)
def q(v): return json.dumps(v)
def frm(sel, t, **v):
    v.setdefault("opacity", 0); v.setdefault("duration", 0.7); v.setdefault("ease", "power3.out")
    J(f'tl.from({q(sel)}, {q(v)}, {t:.3f});')
def to(sel, t, **v): J(f'tl.to({q(sel)}, {q(v)}, {t:.3f});')
def set_(sel, t, **v): J(f'tl.set({q(sel)}, {q(v)}, {t:.3f});')
def fromto(sel, t, a, b): J(f'tl.fromTo({q(sel)}, {q(a)}, {q(b)}, {t:.3f});')
def count(el, t, target, dur, dec, ease="power2.out", comma=False):
    fmt = "o.v.toFixed(%d)" % dec
    if comma: fmt = "Math.round(o.v).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',')"
    J('(function(){var o={v:0},el=document.getElementById(%s);tl.to(o,{v:%s,duration:%s,ease:%s,onUpdate:function(){el.textContent=%s}},%.3f);})();'
      % (q(el), target, dur, q(ease), fmt, t))

# ---------------------------------------------------------------- persistent layers + camera + curtain
set_("#curtain", 0, clipPath="inset(0% 0% 0% 0%)")
fromto("#curtain", 0.25, {"clipPath": "inset(0% 0% 0% 0%)"}, {"clipPath": "inset(0% 0% 0% 100%)", "duration": 0.9, "ease": "power2.inOut"})
for k, m in MID.items():
    fromto("#curtain", m - CUR_HOLD / 2 - CUR_IN, {"clipPath": "inset(0% 100% 0% 0%)"}, {"clipPath": "inset(0% 0% 0% 0%)", "duration": CUR_IN, "ease": "power2.inOut"})
    fromto("#curtain", m + CUR_HOLD / 2, {"clipPath": "inset(0% 0% 0% 0%)"}, {"clipPath": "inset(0% 0% 0% 100%)", "duration": CUR_OUT, "ease": "power2.inOut"})
set_("#curtain", TOTAL - 2.6, clipPath="inset(0% 100% 0% 0%)")
fromto("#curtain", TOTAL - 2.5, {"clipPath": "inset(0% 100% 0% 0%)"}, {"clipPath": "inset(0% 0% 0% 0%)", "duration": 2.3, "ease": "power1.inOut"})  # final fade-to-dark (final scene only)

# ---------------------------------------------------------------- scene markup
H = {}
def sec(k, inner): H[k] = f'<section id="s{k}" class="clip scene" data-start="{WIN[k][0]:.3f}" data-duration="{WIN[k][1]-WIN[k][0]:.3f}" data-track-index="{k}">\n{inner}\n</section>'

# ---- S1: the map  [fact 15]
sec(1, '''
<div id="s1-title" class="plate" style="left:100px;top:90px;padding:30px 44px 34px">
  <div class="kicker">Deforestation seen through digital maps</div>
  <div class="h1" style="margin-top:10px">Reading the Forest</div>
</div>
<div id="s1-legend" class="plate" style="right:100px;bottom:150px;width:640px;padding:24px 30px">
  <div class="kicker" style="margin-bottom:14px">Year of tree cover loss</div>
  <div class="ramp"></div>
  <div class="row between" style="margin-top:10px"><span class="lab">2001 · early</span><span class="lab">2024 · recent</span></div>
</div>
<div id="s1-chip" class="plate" style="left:100px;bottom:150px;padding:22px 34px"><span class="body" style="font-weight:700;color:#F6C453">1 pixel</span><span class="body"> covers about 30 m of ground</span></div>
<div id="s1-q" class="plate" style="left:100px;top:360px;max-width:1080px;padding:36px 48px"><div class="h2">How much forest is being lost, and how do we know?</div></div>
<div class="src" id="s1-src">Map: Hansen et al. (2013), Science 342:850&#8211;853 &#183; UMD / Google / USGS / NASA, Global Forest Change v1.12 (2000&#8211;2024) &#183; displayed in about 300 m cells &#183; tree cover 2000 at least 30% &#183; borders: Natural Earth &#183; dashed line: INPE Legal Amazon</div>''')
frm("#s1-title", 0.9, y=24, duration=1.0)
frm("#s1-legend", st(1, 3) - 0.3, x=40, duration=0.8, ease="expo.out")
frm("#s1-chip", st(1, 5) - 0.2, y=30, duration=0.7)
frm("#s1-q", st(1, 7) - 0.25, y=26, duration=0.9, ease="power2.out")
frm("#s1-src", 2.2, duration=1.2, ease="power1.out")

# ---- S2: what is at stake  [facts 1, 4]
sec(2, '''
<div style="position:absolute;left:120px;top:110px;width:1000px">
  <div class="kicker">World forest area &#183; FAO assessment 2025</div>
  <div style="display:flex;align-items:baseline;gap:30px;margin-top:22px"><div class="num" id="s2-n1" style="font-size:210px">0.00</div><div class="h2" style="color:#EAF1EC">billion hectares</div></div>
  <div class="body" style="margin-top:14px">of forest on Earth</div>
  <div id="s2-bar" style="margin-top:44px"><div class="track"><div class="fill" id="s2-fill" style="width:32%"></div></div>
    <div class="body2" style="margin-top:14px"><b style="color:#F6C453">32%</b> of the global land area &#8211; about one third</div></div>
  <div id="s2-prim" class="plate" style="position:relative;margin-top:50px;padding:24px 40px 28px;display:inline-block"><div class="kicker">At least</div><div style="margin-top:12px"><span class="num" style="font-size:84px">1.18</span><span class="h3"> billion hectares</span></div><div class="body2" style="margin-top:6px">classified as primary forest</div></div>
</div>
<div class="src" id="s2-src">Source: FAO, Global Forest Resources Assessment 2025 &#183; released 21 October 2025 &#183; covers 236 countries and areas</div>''')
frm("#s2-n1", st(2, 1) - 0.2, y=40, duration=0.8)
count("s2-n1", st(2, 1) - 0.1, 4.14, 2.6, 2)
frm("#s2-bar", st(2, 2) - 0.3, x=-40, duration=0.8)
fromto("#s2-fill", st(2, 2) - 0.1, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1, "duration": 1.6, "ease": "power2.out"})
frm("#s2-prim", st(2, 3) - 0.3, y=36, duration=0.8, ease="expo.out")
frm("#s2-src", st(2, 4) - 0.2, duration=0.9)

# ---- S3: how a satellite sees a forest  [facts 13, 14, 15]
cells = "".join('<i class="cell%s"></i>' % (" hot" if i == 18 else "") for i in range(49))
sec(3, '''
<div class="kicker" style="position:absolute;left:120px;top:90px">How a satellite sees a forest</div>
<div id="s3-landsat" class="plate card" style="left:120px;top:150px;width:800px;height:295px">
  <div class="kicker">Landsat (NASA / USGS)</div><div class="num" style="font-size:110px;margin-top:6px">1972</div>
  <div class="body2" style="margin-top:6px">Landsat 1 launched 23 July 1972 &#183; images of Earth's land surface acquired continuously since</div></div>
<div id="s3-sent" class="plate card" style="left:980px;top:150px;width:820px;height:295px">
  <div class="kicker">Sentinel-2 (ESA)</div><div class="num" style="font-size:110px;margin-top:6px">10 m</div>
  <div class="body2" style="margin-top:6px">resolution &#183; revisits the same ground about every 5 days &#183; 290 km swath</div></div>
<div id="s3-grid" class="plate card" style="left:120px;top:480px;width:560px;height:510px;padding:30px 40px">
  <div class="grid">''' + cells + '''</div><div class="body2" style="margin-top:20px"><b style="color:#F6C453">One cell</b> = about 30 m &#215; 30 m</div></div>
<div id="s3-def1" class="plate card" style="left:740px;top:480px;width:1060px;height:215px">
  <div class="kicker">Tree cover</div><div class="h3" style="margin-top:8px;font-size:38px">Canopy closure of vegetation taller than 5 m</div></div>
<div id="s3-def2" class="plate card" style="left:740px;top:720px;width:1060px;height:215px">
  <div class="kicker">Loss</div><div class="h3" style="margin-top:8px;font-size:38px">A stand-replacement disturbance: a change from forest to non-forest</div></div>
<div class="src" id="s3-src">Sources: USGS, Landsat 1 &#183; ESA, Sentinel-2 &#183; Hansen et al. (2013), Global Forest Change v1.12 &#183; Global Forest Watch uses the Hansen dataset</div>''')
frm("#s3-landsat", st(3, 2) - 0.3, y=40, duration=0.8)
frm("#s3-sent", st(3, 4) - 0.3, y=40, duration=0.8, ease="expo.out")
frm("#s3-grid", st(3, 5) - 0.2, scale=0.92, duration=0.8, ease="power2.out")
frm("#s3-def1", st(3, 6) + 3.4, x=50, duration=0.8)
frm("#s3-def2", st(3, 7) - 0.2, x=50, duration=0.8, ease="expo.out")
to("#s3-grid .hot", st(3, 9), scale=1.25, duration=0.5, ease="back.out(2)")
frm("#s3-src", st(3, 2), duration=0.9, ease="power1.out")

# ---- S4: three systems, three questions  [facts 1, 6, 10]
def card4(i, name, who, measures, covers):
    return f'''<div id="s4-c{i}" class="plate card" style="left:{120 + (i - 1) * 590}px;top:300px;width:560px;height:470px;padding:34px 38px">
  <div class="kicker">{who}</div><div class="h3" style="margin-top:8px;font-size:48px">{name}</div>
  <div class="kicker" style="margin-top:34px">Measures</div><div class="body2">{measures}</div>
  <div class="kicker" style="margin-top:26px">Covers</div><div class="body2">{covers}</div></div>'''
sec(4, '''
<div id="s4-h" class="h2" style="position:absolute;left:120px;top:100px;width:1500px">No single number, because there is no single question</div>
''' + card4(1, "Forest Resources Assessment", "FAO", "Figures reported by countries", "236 countries and areas")
    + card4(2, "Tree cover loss", "Global Forest Watch &#183; University of Maryland", "Satellite-detected loss, including loss from fire", "Global")
    + card4(3, "PRODES", "INPE &#183; Brazil's space agency", "Satellite-mapped deforestation", "Brazilian Legal Amazon only") + '''
<div id="s4-ban" class="h3" style="position:absolute;left:120px;top:830px;color:#F6C453;font-size:46px">Different questions give different numbers. Never put them on one axis.</div>
<div class="src" id="s4-src">Sources: FAO, Global Forest Resources Assessment 2025 &#183; Global Forest Review (WRI / University of Maryland) &#183; INPE TerraBrasilis</div>''')
frm("#s4-h", st(4, 1) - 0.2, y=30, duration=0.9)
frm("#s4-c1", st(4, 2) - 0.2, y=50, duration=0.8)
frm("#s4-c2", st(4, 3) - 0.2, y=50, duration=0.8, ease="expo.out")
frm("#s4-c3", st(4, 4) - 0.2, y=50, duration=0.8, ease="power2.out")
frm("#s4-ban", st(4, 5) - 0.1, y=20, duration=0.8)
frm("#s4-src", st(4, 6) - 0.3, duration=0.9, ease="power1.out")

# ---- S5: global trend according to FAO  [facts 2, 3]
SC5 = 56.0  # px per million ha
def bar(id_, label, val, color, top):
    return f'''<div class="brow" style="top:{top}px;left:120px"><div class="blab" id="{id_}-l">{label}</div><div class="bar" id="{id_}" style="width:{round(val * SC5)}px;background:{color}"></div><div class="bval num" id="{id_}-v" style="color:{color}">{val:g}</div></div>'''
sec(5, '''
<div id="s5-h" class="h2" style="position:absolute;left:120px;top:96px">The global trend, according to the FAO</div>
<div class="kicker" id="s5-ga" style="position:absolute;left:120px;top:236px">Deforestation &#183; million hectares per year</div>
''' + bar("s5-b1", "1990&#8211;2000", 17.6, "#F6C453", 290) + bar("s5-b2", "2015&#8211;2025", 10.9, "#F6C453", 380) + '''
<div class="kicker" id="s5-gb" style="position:absolute;left:120px;top:520px">Net forest loss &#183; million hectares per year</div>
''' + bar("s5-b3", "1990s", 10.7, "#EAF1EC", 574) + bar("s5-b4", "2015&#8211;2025", 4.12, "#EAF1EC", 664) + '''
<div id="s5-t1" class="h3" style="position:absolute;left:120px;top:810px;color:#F6C453">Still 10.9 million hectares a year.</div>
<div id="s5-t2" class="body" style="position:absolute;left:120px;top:880px">The trend is falling. The loss has not stopped.</div>
<div class="src" id="s5-src">Source: FAO, Global Forest Resources Assessment 2025 (released 21 October 2025) &#183; net loss = deforestation minus forest gain</div>''')
frm("#s5-h", st(5, 1) - 0.2, y=30, duration=0.9)
frm("#s5-ga", st(5, 2) - 0.3, x=-30, duration=0.7)
for bid, t in (("s5-b2", st(5, 2) + 5.2), ("s5-b1", st(5, 3) + 0.2), ("s5-b3", st(5, 4) + 4.2), ("s5-b4", st(5, 4) + 8.2)):
    if bid == "s5-b3": frm("#s5-gb", t - 1.0, x=-30, duration=0.7)
    fromto("#" + bid, t, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1, "duration": 1.3, "ease": "power3.out"})
    frm(f"#{bid}-l", t - 0.2, x=-12, duration=0.5, ease="power2.out")
    frm(f"#{bid}-v", t + 0.5, x=-12, duration=0.6, ease="power2.out")
to("#s5-b2-v", st(5, 5), scale=1.25, transformOrigin="0% 50%", duration=0.5, ease="back.out(2)")
frm("#s5-t1", st(5, 5) + 0.5, y=20, duration=0.8)
frm("#s5-t2", st(5, 6) - 0.1, y=20, duration=0.8, ease="power2.out")
frm("#s5-src", st(5, 2), duration=0.9, ease="power1.out")

# ---- S6: zoom into the Amazon; the baked timelapse (2001-2024) holds the map  [facts 10, 15]
sec(6, '''
<div id="s6-year" class="plate" style="left:100px;bottom:150px;padding:20px 40px 26px"><div class="kicker">Cumulative tree cover loss, up to</div><div class="num" id="s6-yr" style="font-size:150px;color:#EAF1EC">2001</div></div>
<div id="s6-legend" class="plate" style="right:100px;bottom:150px;width:640px;padding:24px 30px">
  <div class="kicker" style="margin-bottom:14px">Year of loss</div><div class="ramp"></div>
  <div class="row between" style="margin-top:10px"><span class="lab">2001 · early</span><span class="lab">2024 · recent</span></div></div>
<div id="s6-key" class="plate" style="right:100px;top:90px;padding:22px 32px;max-width:760px"><span class="dash"></span><span class="body2"> Brazilian Legal Amazon &#183; area monitored by INPE</span></div>
<div id="s6-note" class="plate" style="left:100px;top:90px;padding:22px 32px;max-width:700px"><div class="body2">Shows <b style="color:#F6C453">where</b> loss happened, not year-to-year totals</div></div>
<div id="s6-poly" class="plate" style="left:100px;bottom:430px;padding:20px 38px 24px;max-width:760px"><div class="num" id="s6-pn" style="font-size:96px">0</div><div class="body2">polygons in INPE's yearly deforestation layer, each with a date and an area</div></div>
<div class="src" id="s6-src">Map: Hansen et al. (2013), Global Forest Change v1.12 &#183; INPE TerraBrasilis, PRODES yearly deforestation layer (polygon count queried 6 October 2026)</div>''')
frm("#s6-year", T6 - 0.2, y=30, duration=0.8)
J('(function(){var o={t:0},el=document.getElementById("s6-yr");tl.to(o,{t:19.2,duration:19.2,ease:"none",onUpdate:function(){el.textContent=2001+Math.min(23,Math.floor(o.t/0.8))}},%.3f);})();' % T6)
frm("#s6-key", st(6, 2) - 0.1, x=40, duration=0.8, ease="expo.out")
frm("#s6-note", st(6, 3) - 0.1, y=-20, duration=0.8)
frm("#s6-legend", T6 + 0.3, y=30, duration=0.8)
frm("#s6-poly", st(6, 6) - 0.2, y=30, duration=0.9)
count("s6-pn", st(6, 6), 835278, 3.2, 0, ease="power2.out", comma=True)
frm("#s6-src", st(6, 4), duration=0.9, ease="power1.out")

# ---- S7: INPE numbers  [facts 8, 9]
sec(7, '''
<div class="kicker" style="position:absolute;left:120px;top:90px">Deforestation in the Brazilian Legal Amazon &#183; INPE PRODES</div>
<div style="position:absolute;left:120px;top:150px;width:1000px;display:flex;flex-direction:column;gap:30px">
<div id="s7-c1" class="plate card" style="position:relative;padding:30px 44px 26px">
  <div class="kicker">August 2023 to July 2024 &#183; estimate</div>
  <div style="display:flex;align-items:baseline;gap:22px;margin-top:8px"><div class="num" id="s7-n1" style="font-size:160px">0</div><div class="h2">km&#178;</div></div></div>
<div id="s7-c2" class="plate card" style="position:relative;padding:30px 44px 26px">
  <div class="kicker">August 2024 to July 2025 &#183; first estimate, October 2025</div>
  <div class="row" style="align-items:baseline;gap:22px;margin-top:8px"><div class="num" id="s7-n2" style="font-size:160px">0</div><div class="h2">km&#178;</div></div>
  <div id="s7-cons" style="margin-top:12px;border-top:1px solid rgba(234,241,236,.18);padding-top:14px"><div class="row" style="align-items:baseline;gap:20px"><span class="num" style="font-size:72px;color:#EAF1EC">5,731 km&#178;</span><span class="body2">consolidated, March 2026</span></div><div class="body2" style="margin-top:2px;color:#9FB3A6">65 km&#178; lower than the estimate (1.12%)</div></div></div>
</div>
<div id="s7-ban" class="h3" style="position:absolute;left:1180px;top:520px;width:640px;color:#F6C453;line-height:1.2">An estimate and a consolidated figure are different versions. Say which one you use.</div>
<div class="src" id="s7-src">Source: INPE, PRODES Legal Amazon: 2024 estimate (data.inpe.br) &#183; 2025 estimate and consolidated data, BiomasBR (3 March 2026)</div>''')
frm("#s7-c1", st(7, 1) - 0.3, y=40, duration=0.8)
frm("#s7-n1", st(7, 1) + 5.9, y=24, duration=0.6)
count("s7-n1", st(7, 1) + 6.0, 6288, 2.2, 0, comma=True)
frm("#s7-c2", st(7, 2) - 0.3, y=40, duration=0.8, ease="expo.out")
frm("#s7-n2", st(7, 2) + 3.2, y=24, duration=0.6)
count("s7-n2", st(7, 2) + 3.3, 5796, 2.2, 0, comma=True)
frm("#s7-cons", st(7, 3) + 3.0, y=20, duration=0.8)
frm("#s7-ban", st(7, 4) - 0.2, x=40, duration=0.8)
frm("#s7-src", st(7, 1), duration=0.9, ease="power1.out")

# ---- S8: fire year  [facts 5, 6, 11, 12]
def bar8(id_, label, val, color, top, left, fmt, scale):
    return f'<div class="brow" style="top:{top}px;left:{left}px"><div class="blab" id="{id_}-l" style="width:96px">{label}</div><div class="bar" id="{id_}" style="width:{round(val * scale)}px;background:{color}"></div><div class="bval num" id="{id_}-v" style="color:{color};font-size:46px;white-space:nowrap">{fmt}</div></div>'
def col(left, chips):
    return f'<div style="position:absolute;left:{left}px;top:390px;width:780px;display:flex;flex-direction:column;gap:16px">' + "".join(chips) + '</div>'
chip8 = lambda id_, text, hot=False: f'<div id="{id_}" class="chip{" hot" if hot else ""}" style="position:relative;width:fit-content">{text}</div>'
sec(8, '''
<div class="kicker" style="position:absolute;left:120px;top:84px">Tropical primary forest loss</div>
<div class="body2" style="position:absolute;left:120px;top:122px;color:#9FB3A6;font-size:26px">Global Forest Watch, University of Maryland data</div>
<div class="kicker" style="position:absolute;left:1000px;top:84px">All tree cover loss, worldwide</div>
<div class="body2" style="position:absolute;left:1000px;top:122px;color:#9FB3A6;font-size:26px">A different measure: not comparable with the left side</div>
''' + bar8("s8-a1", "2024", 6.7, "#F6C453", 190, 120, "6.7 million ha", 40) + bar8("s8-a2", "2025", 4.3, "#EAF1EC", 270, 120, "4.3 million ha", 40)
    + bar8("s8-b1", "2024", 30, "#F6C453", 190, 1000, "about 30 million ha", 9) + bar8("s8-b2", "2025", 25.5, "#EAF1EC", 270, 1000, "25.5 million ha", 9)
    + col(120, [chip8("s8-a-x1", "Nearly twice 2023"), chip8("s8-a-x2", "Fires: nearly 50%. First time the leading cause, ahead of agriculture"),
                chip8("s8-a-x3", "Brazil: 42% of the loss. Fires caused 66% of Brazil's"), chip8("s8-a-x4", "2025: 36% lower than 2024", True), chip8("s8-a-x5", "Still 46% higher than a decade earlier", True)])
    + col(1000, [chip8("s8-b-x1", "2024: 5% more than 2023"), chip8("s8-b-x2", "2025: 14% lower than 2024", True), chip8("s8-b-x3", "Fires: 42% of the 2025 loss"), chip8("s8-b-x4", "An area larger than the United Kingdom")])
    + '''
<div class="src" id="s8-src">Sources: WRI / Global Forest Watch, 2024 tree cover loss release &#183; Global Forest Review, 2025 analysis (updated 29 April 2026) &#183; data: University of Maryland GLAD lab</div>''')
for bid, t in (("s8-a1", st(8, 2) + 7.0), ("s8-a2", st(8, 5) + 4.0), ("s8-b1", st(8, 7) + 6.0), ("s8-b2", st(8, 8) + 4.0)):
    fromto("#" + bid, t, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1, "duration": 1.3, "ease": "power3.out"})
    frm(f"#{bid}-l", t - 0.2, x=-12, duration=0.5, ease="power2.out")
    frm(f"#{bid}-v", t + 0.5, x=-14, duration=0.6, ease="power2.out")
for sel, t in (("#s8-a-x1", st(8, 2) + 10.0), ("#s8-a-x2", st(8, 3) + 3.2), ("#s8-a-x3", st(8, 4) + 0.2), ("#s8-a-x4", st(8, 5) + 6.0), ("#s8-a-x5", st(8, 6) + 0.2),
               ("#s8-b-x1", st(8, 7) + 9.0), ("#s8-b-x2", st(8, 8) + 6.0), ("#s8-b-x3", st(8, 9)), ("#s8-b-x4", st(8, 10))):
    frm(sel, t - 0.1, x=-36, duration=0.7, ease="power3.out")
frm("#s8-src", st(8, 1), duration=0.9, ease="power1.out")

# ---- S9: closing; return to the opening image  [fact 7]
sec(9, '''
<div id="s9-p1" class="plate" style="left:100px;top:90px;padding:30px 48px"><div class="h1" style="font-size:76px">Measured. Mapped. Public.</div></div>
<div id="s9-p2" class="plate" style="right:100px;top:300px;width:760px;padding:30px 42px"><div class="h3" style="line-height:1.22">In 2025, deforestation was <b style="color:#F6C453">70% higher</b> than the level needed to halt and reverse forest loss by 2030</div><div class="body2" style="margin-top:12px;color:#9FB3A6">Global Forest Review, WRI (April 2026)</div></div>
<div id="s9-p3" class="plate" style="left:100px;bottom:150px;padding:30px 48px;max-width:1500px"><div class="h2">A map cannot protect a forest.</div><div id="s9-p3b" class="h3" style="margin-top:10px;color:#F6C453">But it can show whether we keep our promises.</div></div>
<div class="src" id="s9-src">Map: Hansen et al. (2013), Global Forest Change v1.12 &#183; tree cover loss 2001&#8211;2024 &#183; dashed line: INPE Legal Amazon</div>''')
frm("#s9-p1", st(9, 2) - 0.2, y=26, duration=0.9)
frm("#s9-p2", st(9, 3) - 0.2, x=50, duration=0.9, ease="expo.out")
frm("#s9-p3", st(9, 5) - 0.2, y=30, duration=0.9)
frm("#s9-p3b", st(9, 6) - 0.2, y=16, duration=0.8, ease="power2.out")
frm("#s9-src", st(9, 1), duration=0.9, ease="power1.out")

# ---- S10: sources (final scene; the only one that fades out)
SRC = [("FAO", "Global Forest Resources Assessment 2025, released 21 October 2025", "fao.org/newsroom"),
       ("WRI / Global Forest Watch", "Global Forest Loss Shatters Records in 2024, Fueled by Massive Fires", "wri.org/news"),
       ("WRI", "Global Forest Review, 2025 analysis, updated 29 April 2026", "gfr.wri.org/latest-analysis-deforestation-trends"),
       ("Hansen et al. (2013)", "Science 342:850&#8211;853 &#183; Global Forest Change v1.12 (UMD, Google, USGS, NASA)", "storage.googleapis.com/earthenginepartners-hansen"),
       ("INPE", "PRODES Legal Amazon, 2024 estimate", "data.inpe.br"),
       ("INPE / BiomasBR", "PRODES 2025 estimate and consolidated data, 3 March 2026", "data.inpe.br/biomasbr"),
       ("INPE TerraBrasilis", "Yearly deforestation layer, queried 6 October 2026", "terrabrasilis.dpi.inpe.br"),
       ("USGS", "Landsat 1", "usgs.gov/landsat-missions/landsat-1"),
       ("ESA", "Sentinel-2", "esa.int"),
       ("Natural Earth", "Country boundaries (public domain)", "naturalearthdata.com")]
rows = "".join(f'<div class="srow"><div class="sname">{a}</div><div class="sdesc">{b}</div><div class="surl">{c}</div></div>' for a, b, c in SRC)
sec(10, '<div id="s10-all"><div class="h2" id="s10-h" style="position:absolute;left:100px;top:70px">Sources</div><div class="kicker" style="position:absolute;right:100px;top:96px">All figures accessed 6 October 2026</div>'
        '<div id="s10-list" style="position:absolute;left:100px;top:170px;width:1720px">' + rows + '</div>'
        '<div id="s10-not" class="plate" style="left:100px;top:815px;width:1720px;padding:22px 34px"><div class="kicker">What this film does not claim</div>'
        '<div class="body2" style="font-size:25px;line-height:1.3;margin-top:6px">Causes of clearing, regions not shown, or policy effects. The map shows tree cover loss (including fire), a different measure from INPE PRODES or FAO deforestation. Display cells are about 300 m; early-year detection differs from later years, so the map shows where, not annual totals.</div></div></div>')
frm("#s10-h", MID[9] + 0.8, y=20, duration=0.8)
J('tl.from("#s10-list .srow", {opacity:0, x:-30, duration:0.6, ease:"power3.out", stagger:0.55}, %.3f);' % (st(10, 1) - 0.1))
frm("#s10-not", st(10, 2) + 4.0, y=24, duration=0.9, ease="power2.out")

# ---------------------------------------------------------------- page
CSS = '''
@font-face{font-family:"DM Sans";src:url("assets/fonts/DMSans-400.woff2") format("woff2");font-weight:400}
@font-face{font-family:"DM Sans";src:url("assets/fonts/DMSans-500.woff2") format("woff2");font-weight:500}
@font-face{font-family:"DM Sans";src:url("assets/fonts/DMSans-700.woff2") format("woff2");font-weight:700}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#07110D}
body{font-family:"DM Sans",sans-serif;color:#EAF1EC;font-variant-numeric:tabular-nums}
#root{position:relative;width:100%;height:100%;overflow:hidden;background:#07110D}
#ground{position:absolute;inset:0;width:1920px;height:1080px;z-index:0}
.scene{position:absolute;inset:0;z-index:10}
#curtain{position:absolute;inset:0;background:#07110D;z-index:100}
.plate{position:absolute;background:rgba(7,17,13,.86);border:1px solid rgba(234,241,236,.16);border-radius:22px}
.card{padding:30px 40px}
.kicker{font-size:24px;letter-spacing:.14em;text-transform:uppercase;color:#9FB3A6;font-weight:500}
.h1{font-size:84px;font-weight:700;line-height:1.04;letter-spacing:-.01em}
.h2{font-size:60px;font-weight:700;line-height:1.1;letter-spacing:-.005em}
.h3{font-size:42px;font-weight:700;line-height:1.15}
.body{font-size:40px;font-weight:500;line-height:1.25}
.body2{font-size:30px;font-weight:400;line-height:1.3;color:#EAF1EC}
.lab{font-size:24px;color:#9FB3A6;font-weight:500}
.num{font-weight:700;line-height:1.2;color:#F6C453;letter-spacing:-.02em}
.row{display:flex}.between{justify-content:space-between}
.src{position:absolute;left:100px;right:100px;bottom:36px;font-size:22px;line-height:1.35;color:#9FB3A6;background:rgba(7,17,13,.86);padding:10px 18px;border-radius:12px}
.ramp{height:26px;border-radius:13px;background:linear-gradient(90deg,#F6C453,#F08A3C,#D9482B,#9E1B32)}
.track{height:26px;border-radius:13px;background:rgba(234,241,236,.14);width:900px;overflow:hidden}.fill{height:100%;background:#F6C453;border-radius:13px}
.grid{display:grid;grid-template-columns:repeat(7,50px);gap:6px}.cell{display:block;width:50px;height:50px;border-radius:6px;background:#1D4D39}.cell.hot{background:#F08A3C}
.brow{position:absolute;display:flex;align-items:center;gap:18px;height:56px}
.blab{width:200px;font-size:30px;color:#9FB3A6;font-weight:500}
.bar{height:46px;border-radius:8px}.bval{font-size:48px}
.chip{position:absolute;background:rgba(7,17,13,.86);border:1px solid rgba(234,241,236,.16);border-radius:16px;padding:14px 26px;font-size:32px;font-weight:500;line-height:1.2;max-width:780px}
.chip.hot{border-color:#F6C453;color:#F6C453}
.dash{display:inline-block;width:70px;border-top:5px dashed #EAF1EC;vertical-align:middle}
.srow{display:grid;grid-template-columns:380px 1fr 640px;gap:20px;font-size:25px;line-height:1.25;padding:8px 0;border-bottom:1px solid rgba(234,241,236,.12)}
.sname{font-weight:700;color:#EAF1EC}.sdesc{color:#EAF1EC}.surl{color:#9FB3A6;font-size:23px;text-align:right}
'''
audio = f'<audio id="narration" src="assets/narration.wav" data-start="0" data-duration="{TOTAL}" data-track-index="30" data-volume="1"></audio>'
ground = f'<video id="ground" class="clip" src="assets/ground.mp4" data-start="0" data-duration="{TOTAL}" data-track-index="0" muted playsinline></video>'
body = ground + "\n" + "\n".join(H[k] for k in range(1, 11)) + '\n<div id="curtain"></div>\n' + audio
html = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080"><title>Reading the Forest</title>
<script src="gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
{body}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body></html>'''
open(f"{ROOT}/video/index.html", "w", encoding="utf-8").write(html)
print("wrote video/index.html", len(html), "bytes; duration", TOTAL)
