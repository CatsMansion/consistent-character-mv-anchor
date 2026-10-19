# Consistent Character MV Anchor

A reusable methodology for producing **consistent character anchors and
animation / MV assets** for one fixed original character:

- **i2i + locked anchor** keeps identity stable across poses / expressions / frames.
- **Green-screen keying** (dual criteria) turns a solid background transparent and
  also strips light-colored generator watermarks on the background.
- **Programmatic feature locking** holds small features (hair streak, earring) the
  model drifts on — no extra generations.
- **Frame-consistency locking** is the only reliable way to get absolute
  pixel consistency across frames (lock the static region, animate only the rest).
- **Composition baseline** measurement keeps assets from jumping in a sprite pack.

This is a methodology, not a model. Plug in whatever image-to-image / keying
tools you already use.

## Install
```bash
pip install Pillow
```

## Usage
```bash
# measure a reference frame's composition baseline (do this once on the anchor)
python scripts/measure_bbox.py anchor.png

# chroma-key a generated frame to transparent (background + disconnected
# specks / background watermarks are dropped via largest-component cleanup)
python scripts/key_green.py frame.png frame_keyed.png --key "#06EB0D" --dist 60
```

## Ethics
Use your own original characters. Never publish or process client / third-party
assets through a shared pipeline. Strip only the in-file watermark from images
you generated, and keep AI-use disclosure separate per platform rules.

## License
MIT
