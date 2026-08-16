from __future__ import annotations

import html
import math
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

GIF.mkdir(parents=True, exist_ok=True)
SHEETS.mkdir(parents=True, exist_ok=True)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def create_gifs() -> None:
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
        if transparent_preview:
            tile = checkerboard(preview_size)
        else:
            tile = Image.new("RGB", preview_size, "#F8FAFC")
        image = Image.open(path).convert("RGBA")
        image.thumbnail((preview_size[0] - 12, preview_size[1] - 12), Image.Resampling.LANCZOS)
        px = (preview_size[0] - image.width) // 2
        py = (preview_size[1] - image.height) // 2
        tile.paste(image, (px, py), image)
        sheet.paste(tile, (x0 + 10, y0 + 10))
        label = path.stem
        draw.text((x0 + 14, y0 + tile_size[1] - 25), label, fill="#0F172A", font=font)
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


if __name__ == "__main__":
    create_gifs()
    make_contact_sheet(STATIC, SHEETS / "static-gallery.png")
    make_contact_sheet(
        TRANSPARENT,
        SHEETS / "transparent-gallery.png",
        transparent_preview=True,
    )
    create_html()
