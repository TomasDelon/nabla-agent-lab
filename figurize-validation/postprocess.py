from __future__ import annotations

import hashlib
import html
import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
VIDEO = OUTPUT / "video"
GIF = OUTPUT / "gif"
STATIC = OUTPUT / "static"
TRANSPARENT = OUTPUT / "transparent"
SHEETS = OUTPUT / "contact_sheets"

EXPECTED_STATIC = 21
EXPECTED_TRANSPARENT = 7
EXPECTED_VIDEO = 4
EXPECTED_GIF = 4

GIF.mkdir(parents=True, exist_ok=True)
SHEETS.mkdir(parents=True, exist_ok=True)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def create_gifs() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required for GIF post-processing")
    for video in sorted(VIDEO.glob("*.mp4")):
        palette = GIF / f"{video.stem}_palette.png"
        output = GIF / f"{video.stem}.gif"
        run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(video),
                "-vf",
                "fps=12,scale=720:-1:flags=lanczos,palettegen=max_colors=192",
                str(palette),
            ]
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(video),
                "-i",
                str(palette),
                "-lavfi",
                "fps=12,scale=720:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
                str(output),
            ]
        )
        palette.unlink(missing_ok=True)


def checkerboard(size: tuple[int, int], square: int = 22) -> Image.Image:
    canvas = Image.new("RGB", size, "#F8FAFC")
    draw = ImageDraw.Draw(canvas)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill="#E2E8F0")
    return canvas


def make_contact_sheet(
    source: Path,
    destination: Path,
    *,
    columns: int = 3,
    tile_size: tuple[int, int] = (480, 305),
    transparent_preview: bool = False,
) -> None:
    images = sorted(source.glob("*.png"))
    if not images:
        return
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGB", (columns * tile_size[0], rows * tile_size[1]), "#E2E8F0")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, path in enumerate(images):
        col = index % columns
        row = index // columns
        x0 = col * tile_size[0]
        y0 = row * tile_size[1]
        preview_size = (tile_size[0] - 20, tile_size[1] - 45)
        tile = checkerboard(preview_size) if transparent_preview else Image.new("RGB", preview_size, "#F8FAFC")
        image = Image.open(path).convert("RGBA")
        image.thumbnail((preview_size[0] - 12, preview_size[1] - 12), Image.Resampling.LANCZOS)
        px = (preview_size[0] - image.width) // 2
        py = (preview_size[1] - image.height) // 2
        tile.paste(image, (px, py), image)
        sheet.paste(tile, (x0 + 10, y0 + 10))
        draw.text(
            (x0 + 14, y0 + tile_size[1] - 25),
            path.stem,
            fill="#0F172A",
            font=font,
        )
    sheet.save(destination, optimize=True)


def create_html() -> None:
    static_items = "\n".join(
        f'<figure><img src="static/{html.escape(path.name)}"><figcaption>{html.escape(path.stem)}</figcaption></figure>'
        for path in sorted(STATIC.glob("*.png"))
    )
    transparent_items = "\n".join(
        f'<figure class="checker"><img src="transparent/{html.escape(path.name)}"><figcaption>{html.escape(path.stem)}</figcaption></figure>'
        for path in sorted(TRANSPARENT.glob("*.png"))
    )
    gif_items = "\n".join(
        f'<figure><img src="gif/{html.escape(path.name)}"><figcaption>{html.escape(path.stem)}</figcaption></figure>'
        for path in sorted(GIF.glob("*.gif"))
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figurize Manim validation gallery</title>
<style>
body{{font-family:system-ui,sans-serif;background:#e2e8f0;color:#0f172a;margin:0;padding:32px}}
main{{max-width:1400px;margin:auto}}
h1{{margin-top:0}}h2{{margin-top:44px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}}
figure{{margin:0;background:#f8fafc;border-radius:14px;padding:12px;box-shadow:0 3px 14px #0f172a18}}
figure.checker{{background-color:#f8fafc;background-image:linear-gradient(45deg,#e2e8f0 25%,transparent 25%),linear-gradient(-45deg,#e2e8f0 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e2e8f0 75%),linear-gradient(-45deg,transparent 75%,#e2e8f0 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}}
img{{display:block;width:100%;height:auto;border-radius:8px}}
figcaption{{padding:10px 4px 2px;font-family:ui-monospace,monospace;font-size:13px}}
</style>
</head><body><main>
<h1>Figurize Manim validation gallery</h1>
<p>All visual media below was rendered from the Manim source in this package.</p>
<h2>Static scenes</h2><section class="grid">{static_items}</section>
<h2>Transparent exports</h2><section class="grid">{transparent_items}</section>
<h2>Animations</h2><section class="grid">{gif_items}</section>
</main></body></html>"""
    (OUTPUT / "index.html").write_text(document, encoding="utf-8")


def write_manifest() -> dict[str, object]:
    files = []
    for path in sorted(
        p for p in OUTPUT.rglob("*") if p.is_file() and "logs" not in p.parts
    ):
        files.append(
            {
                "path": path.relative_to(OUTPUT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    manifest: dict[str, object] = {
        "renderer": "Manim Community v0.20.1",
        "static_count": len(list(STATIC.glob("*.png"))),
        "transparent_count": len(list(TRANSPARENT.glob("*.png"))),
        "video_count": len(list(VIDEO.glob("*.mp4"))),
        "gif_count": len(list(GIF.glob("*.gif"))),
        "contact_sheet_count": len(list(SHEETS.glob("*.png"))),
        "files": files,
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def validate(manifest: dict[str, object]) -> None:
    assert manifest["static_count"] == EXPECTED_STATIC, manifest
    assert manifest["transparent_count"] == EXPECTED_TRANSPARENT, manifest
    assert manifest["video_count"] == EXPECTED_VIDEO, manifest
    assert manifest["gif_count"] == EXPECTED_GIF, manifest
    assert manifest["contact_sheet_count"] == 2, manifest
    assert (OUTPUT / "index.html").is_file()


if __name__ == "__main__":
    create_gifs()
    make_contact_sheet(STATIC, SHEETS / "static-gallery.png")
    make_contact_sheet(
        TRANSPARENT,
        SHEETS / "transparent-gallery.png",
        transparent_preview=True,
    )
    create_html()
    result = write_manifest()
    validate(result)
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))
