# DESIGN: Reading the Forest

## Style Prompt
Sober, scientific, cinematic. A near-black canvas that reads as a night-time view from orbit; the map is the hero and
everything else is quiet. Motion is slow and deliberate (camera drifts, numbers count up once, nothing bounces).
Reference feel: an observatory briefing, not a news promo.

## Colors
- Canvas: #07110D (near-black green)  - Primary text: #EAF1EC  - Secondary text: #9FB3A6 (>= 4.5:1 on canvas)
- Forest (tree cover 2000): #2F7D4F (muted, behind everything)
- Loss ramp (sequential, one hue family, year 2001 to 2024): #F6C453 -> #F08A3C -> #D9482B -> #9E1B32
- Accent for the single highlighted number: #F6C453

## Typography
- Headings and numbers: DM Sans (700 / 500). Data labels and sources: DM Mono or JetBrains Mono (400), tabular numerals.
- Sizes for 1080p: numbers 120-220 px, headlines 64-84 px, body 34-40 px, source line 24-28 px.

## What NOT to Do
- No stock "green leaf" clip art, no emoji, no drop shadows on text.
- No full-screen linear gradients on the dark canvas (banding): radial or solid only.
- No number without a source and year on screen at the same time.
- No jump cuts; no exit animations except on the final scene (HyperFrames rule).
- Never compare FAO, Global Forest Watch and INPE figures on one chart axis as if they measured the same thing.
