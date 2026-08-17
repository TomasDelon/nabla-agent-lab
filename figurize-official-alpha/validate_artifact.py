from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

root = Path("artifact")
alpha_path = root / "figurize-official-transparent.png"
preview_path = root / "figurize-official-preview.png"
if not alpha_path.is_file() or not preview_path.is_file():
    raise SystemExit("official smoke output is missing")
alpha = Image.open(alpha_path).convert("RGBA").getchannel("A").getextrema()
if alpha[0] == 255:
    raise SystemExit("transparent render has no transparent pixels")
files = []
for path in sorted(p for p in root.iterdir() if p.is_file()):
    files.append(
        {
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
manifest = {
    "renderer": "Manim Community v0.20.1 official Docker image",
    "scene": "FigurizeOfficialSmoke",
    "xcharter_text": True,
    "xcharter_math": True,
    "editorial_label_connectors": 0,
    "point_shapes": ["filled_circle"],
    "positive_area_role": "bertault_green",
    "negative_area_role": "bertault_warm_red",
    "secondary_role": "bertault_purple_tangent",
    "transparent_alpha_extrema": alpha,
    "files": files,
}
(root / "manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)
print(json.dumps(manifest, indent=2))
