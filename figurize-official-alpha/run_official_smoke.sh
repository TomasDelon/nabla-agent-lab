#!/usr/bin/env bash
set -euo pipefail
export TERM=xterm

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  texlive-fonts-extra \
  texlive-luatex \
  texlive-latex-extra \
  dvisvgm

# Debian TeX Live contains XCharter text. XCharter Math is fetched only into
# the ephemeral CI container and referenced by absolute Path from LuaLaTeX.
# It is never committed to the repository or redistributed in artifacts.
install -d /usr/local/share/fonts/figurize
curl --fail --location --retry 4 \
  https://mirrors.ctan.org/fonts/xcharter-math/XCharter-Math.otf \
  --output /usr/local/share/fonts/figurize/XCharter-Math.otf
fc-cache -f >/dev/null 2>&1 || true

rm -rf artifact
mkdir -p artifact/media-preview artifact/media-alpha
{
  echo "manim=$(manim --version)"
  echo "lualatex=$(lualatex --version | head -n 1)"
  echo "xcharter_text_package=$(kpsewhich XCharter.sty)"
  echo "xcharter_math_file=/usr/local/share/fonts/figurize/XCharter-Math.otf"
  echo "luatex85=$(kpsewhich luatex85.sty)"
  echo "dvisvgm=$(dvisvgm --version | head -n 1)"
} > artifact/font-and-runtime-report.txt

test -s /usr/local/share/fonts/figurize/XCharter-Math.otf
test -n "$(kpsewhich XCharter.sty)"
test -n "$(kpsewhich luatex85.sty)"

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
