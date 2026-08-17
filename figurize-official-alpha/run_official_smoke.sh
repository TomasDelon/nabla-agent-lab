#!/usr/bin/env bash
set -euo pipefail

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends texlive-fonts-extra
luaotfload-tool --update --force >/dev/null

rm -rf artifact
mkdir -p artifact/media-preview artifact/media-alpha
{
  echo "manim=$(manim --version)"
  echo "lualatex=$(lualatex --version | head -n 1)"
  echo "xcharter_text=$(fc-match XCharter | head -n 1)"
  echo "xcharter_math_file=$(kpsewhich XCharter-Math.otf)"
} > artifact/font-and-runtime-report.txt

manim -ql -s --format=png --disable_caching \
  --media_dir artifact/media-preview \
  -o figurize-official-preview \
  official_smoke.py FigurizeOfficialSmoke

manim -ql -s --format=png --transparent --disable_caching \
  --media_dir artifact/media-alpha \
  -o figurize-official-transparent \
  official_smoke.py FigurizeOfficialSmoke

preview=$(find artifact/media-preview -type f -name 'figurize-official-preview*.png' | head -n 1)
transparent=$(find artifact/media-alpha -type f -name 'figurize-official-transparent*.png' | head -n 1)
test -n "$preview" && test -f "$preview"
test -n "$transparent" && test -f "$transparent"
cp "$preview" artifact/figurize-official-preview.png
cp "$transparent" artifact/figurize-official-transparent.png

python validate_artifact.py
