# Rebuild pipeline: "Reading the Forest"

Needs: Node 22+, ffmpeg, Python 3 with numpy, Pillow, rasterio; `npm install` here; a Fish Audio key in `FISH_API_KEY` (never commit it).

1. Facts: `FACT-SHEET.md` (only VERIFIED rows are used). Script: `SCRIPT.md` (source tags per sentence).
2. Map data (Hansen GFC v1.12 tiles 00N/10S x 070W/060W/050W, lossyear + treecover2000):
   `tools/hansen_downsample.py`, `tools/treecover_downsample.py`, then `tools/render_layers.py` -> `assets/maps/*.png`.
3. Narration: `python3 -I tools/narrate.py` (one clip per sentence, Fish voice 2947ec32..., model s2.1-pro-free) then `python3 -I tools/build_audio.py` -> `video/assets/narration.wav` + `video/cues.json`.
4. Map ground: `python3 -I tools/bake_maps.py <ne_countries.geojson> <legal_amazon.geojson> <seconds>` (makes `video/assets/maps/loss_all.png`), then
   `python3 -I tools/bake_ground.py <ne_countries.geojson> <legal_amazon.geojson>` -> `video/assets/ground.mp4`: the whole map ground (camera moves, dimming under each section, opening reveal,
   push-in to the Amazon, 2001-2024 timelapse) as ONE video. Compositing the 6000x4000 layers live in Chrome ran at 0.25 fps, so the ground is baked; timing lives in `tools/plan.py`.
5. Composition: `python3 -I tools/build_video.py` writes `video/index.html` (edit the generator, not the HTML).
6. Check and render: `cd video && npx hyperframes check && npx hyperframes render --quality standard --output renders/reading-the-forest.mp4`.
