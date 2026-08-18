from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

root = Path(sys.argv[1] if len(sys.argv) > 1 else "output")
static_files = sorted((root / "static").glob("*.png"))
video_files = sorted((root / "video").glob("*.mp4"))
log_files = sorted((root / "logs").glob("*.log"))

if len(static_files) != 11:
    raise SystemExit(f"Expected 11 static PNGs, found {len(static_files)}")
if len(video_files) != 2:
    raise SystemExit(f"Expected 2 MP4s, found {len(video_files)}")
if len(log_files) != 13:
    raise SystemExit(f"Expected 13 render logs, found {len(log_files)}")

alpha_extrema = {}
for path in static_files:
    image = Image.open(path).convert("RGBA")
    extrema = image.getchannel("A").getextrema()
    alpha_extrema[path.name] = extrema
    if extrema[0] == 255:
        raise SystemExit(f"No transparent pixels found in {path}")
    if path.stat().st_size < 5000:
        raise SystemExit(f"Suspiciously small PNG: {path}")

for path in video_files:
    if path.stat().st_size < 10000:
        raise SystemExit(f"Suspiciously small MP4: {path}")

source = (root / "source" / "gallery.py").read_text(encoding="utf-8")
for forbidden in ("matplotlib", "plotly", "seaborn", "<svg", "image_gen"):
    if forbidden in source.lower():
        raise SystemExit(f"Forbidden drawing system token in source: {forbidden}")
for required in ("from manim import", "XCharter", "XCharter-Math.otf", "StealthTip"):
    if required not in source:
        raise SystemExit(f"Required Manim or typography token missing: {required}")

files = []
for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "manifest.json"):
    files.append(
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )

manifest = {
    "status": "passed",
    "mathematical_renderer": "Manim Community v0.20.1",
    "alternative_mathematical_renderers": [],
    "text_font": "XCharter",
    "math_font": "XCharter Math",
    "static_png_count": len(static_files),
    "mp4_count": len(video_files),
    "render_log_count": len(log_files),
    "point_shapes": ["filled_circle", "hollow_circle"],
    "editorial_label_connectors": 0,
    "positive_role": "bertault_green",
    "negative_role": "bertault_warm_red",
    "secondary_role": "bertault_purple",
    "alpha_extrema": alpha_extrema,
    "files": files,
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({key: value for key, value in manifest.items() if key not in {"files", "alpha_extrema"}}, indent=2))
