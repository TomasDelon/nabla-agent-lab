#!/usr/bin/env bash
set -euo pipefail
export TERM=xterm

rm -rf artifact
mkdir -p artifact/media-preview artifact/media-alpha
exec > >(tee artifact/run.log) 2>&1
trap 'status=$?; echo "$status" > artifact/exit-status.txt; exit $status' EXIT

echo "== Figurize official Manim smoke =="
echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  unzip \
  texlive-luatex \
  texlive-latex-extra \
  dvisvgm

# Install XCharter and XCharter Math only in the ephemeral CI container.
# Font files are neither committed nor included in the published artifact.
install -d /usr/local/share/fonts/figurize /tmp/xcharter
curl --fail --location --retry 4 \
  https://mirrors.ctan.org/fonts/xcharter.zip \
  --output /tmp/xcharter.zip
unzip -q /tmp/xcharter.zip -d /tmp/xcharter
find /tmp/xcharter -type f -name '*.otf' -exec cp {} /usr/local/share/fonts/figurize/ \;

curl --fail --location --retry 4 \
  https://mirrors.ctan.org/fonts/xcharter-math/XCharter-Math.otf \
  --output /usr/local/share/fonts/figurize/XCharter-Math.otf

# Manim's LuaLaTeX template imports luatex85. CTAN distributes this package as
# documented sources, so generate luatex85.sty from its .ins/.dtx files.
install -d /usr/local/share/texmf/tex/generic/luatex85 /tmp/luatex85
curl --fail --location --retry 4 \
  https://mirrors.ctan.org/macros/generic/luatex85.zip \
  --output /tmp/luatex85.zip
unzip -q /tmp/luatex85.zip -d /tmp/luatex85
luatex85_ins=$(find /tmp/luatex85 -type f -name 'luatex85.ins' | head -n 1)
test -n "$luatex85_ins" && test -f "$luatex85_ins"
luatex85_dir=$(dirname "$luatex85_ins")
(
  cd "$luatex85_dir"
  tex -interaction=nonstopmode luatex85.ins >/tmp/luatex85-generation.log
)
luatex85_sty=$(find /tmp/luatex85 -type f -name 'luatex85.sty' | head -n 1)
test -n "$luatex85_sty" && test -s "$luatex85_sty"
cp "$luatex85_sty" /usr/local/share/texmf/tex/generic/luatex85/luatex85.sty

# Explicitly expose the compatibility directory to every LuaLaTeX subprocess
# launched by Manim. The trailing colon preserves TeX's normal search path.
export TEXINPUTS="/usr/local/share/texmf/tex/generic/luatex85//:"
mktexlsr /usr/local/share/texmf >/dev/null || true
fc-cache -f >/dev/null 2>&1 || true

{
  echo "manim=$(manim --version)"
  echo "lualatex=$(lualatex --version | head -n 1)"
  echo "xcharter_roman=/usr/local/share/fonts/figurize/XCharter-Roman.otf"
  echo "xcharter_math=/usr/local/share/fonts/figurize/XCharter-Math.otf"
  echo "luatex85=$(kpsewhich luatex85.sty)"
  echo "texinputs=$TEXINPUTS"
  echo "dvisvgm=$(dvisvgm --version | head -n 1)"
} > artifact/font-and-runtime-report.txt

cat artifact/font-and-runtime-report.txt

test -s /usr/local/share/fonts/figurize/XCharter-Roman.otf
test -s /usr/local/share/fonts/figurize/XCharter-Math.otf
test -s /usr/local/share/texmf/tex/generic/luatex85/luatex85.sty
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
echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
