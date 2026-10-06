# Download "Reading the Forest" (1080p)

The full-quality video is 217 MB, so it is stored here in 5 parts (each under 50 MB).

1. Download all five files `reading-the-forest-1080p.mp4.part00` to `.part04` (on GitHub: open each file, then "Download raw file").
2. Put them in one folder and join them:
   - macOS / Linux: `cat reading-the-forest-1080p.mp4.part* > reading-the-forest-1080p.mp4`
   - Windows (Command Prompt, inside the folder): `copy /b reading-the-forest-1080p.mp4.part00+reading-the-forest-1080p.mp4.part01+reading-the-forest-1080p.mp4.part02+reading-the-forest-1080p.mp4.part03+reading-the-forest-1080p.mp4.part04 reading-the-forest-1080p.mp4`
3. Check the join (optional): the SHA-256 of the joined file must match `reading-the-forest-1080p.sha256`.
   - macOS: `shasum -a 256 reading-the-forest-1080p.mp4` &nbsp; Linux: `sha256sum ...` &nbsp; Windows: `certutil -hashfile reading-the-forest-1080p.mp4 SHA256`

Video: 1920x1080, 30 fps, 7 min 21 s, H.264 + AAC. Captions: `../video/reading-the-forest.srt`.
