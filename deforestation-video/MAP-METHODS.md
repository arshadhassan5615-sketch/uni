# Map methods (shown on the final slide)

- Data: Global Forest Change v1.12 (2000-2024), Hansen/UMD/Google/USGS/NASA. Tiles 00N/10S x 070W/060W/050W (lon -70..-40, lat 0..-20).
- Source pixels ~30 m. For display they were aggregated into ~300 m cells (10x10 blocks): a cell shows loss if >= 12/255 (~5%) of its pixels were lost
  in one year; its colour is the mean loss year of those pixels.
- Loss is shown only where the 2000 cell-mean canopy cover was >= 30% (the dataset's standard forest threshold). This keeps Cerrado savanna and non-forest land off the map.
- "Loss" is stand-replacement disturbance. It includes fire, clearing, storms and plantation harvest. It is NOT the same as INPE PRODES deforestation or FAO deforestation.
- Early-year detection in this dataset is not equivalent to later years (sensor and method changes from 2011 onward are documented by the authors),
  so the animation shows WHERE loss happened, never a year-to-year total.
- Boundaries: Natural Earth country borders (public domain); Brazilian Legal Amazon outline from INPE TerraBrasilis.
- Code: tools/hansen_downsample.py, tools/treecover_downsample.py, tools/render_layers.py.
