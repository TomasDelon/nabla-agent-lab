#!/usr/bin/env bash
set -euo pipefail
export TERM=xterm

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  dvisvgm \
  texlive-fonts-extra \
  texlive-latex-extra \
  texlive-latex-recommended \
  texlive-xetex

install -d /usr/local/share/fonts/figurize
curl --fail --location --retry 5 \
  https://mirrors.ctan.org/fonts/xcharter-math/XCharter-Math.otf \
  --output /usr/local/share/fonts/figurize/XCharter-Math.otf
test -s /usr/local/share/fonts/figurize/XCharter-Math.otf
fc-cache -f >/dev/null 2>&1 || true

rm -rf output media
mkdir -p output/static output/video output/logs output/source

STATIC_SCENES=(
  SignedAreaScene
  FunctionRootsTangentsScene
  IntervalScene
  PointVectorScene
  TriangleScene
  ProbabilityScene
  ScatterScene
  HistogramScene
  UnitCircleScene
  SurfaceTangentPlaneScene
  HelixScene
)

for scene in "${STATIC_SCENES[@]}"; do
  echo "Rendering $scene"
  manim -ql -s --format=png --transparent --disable_caching \
    --media_dir media \
    -o "$scene" \
    gallery.py "$scene" \
    >"output/logs/$scene.log" 2>&1
  rendered=$(find media -type f -name "$scene*.png" | sort | tail -n 1)
  test -n "$rendered" && test -f "$rendered"
  cp "$rendered" "output/static/$scene.png"
done

ANIMATIONS=(LinearTransformAnimationScene SignedAreaAnimationScene)
for scene in "${ANIMATIONS[@]}"; do
  echo "Rendering animation $scene"
  manim -ql --disable_caching \
    --media_dir media \
    -o "$scene" \
    gallery.py "$scene" \
    >"output/logs/$scene.log" 2>&1
  rendered=$(find media -type f -name "$scene*.mp4" | sort | tail -n 1)
  test -n "$rendered" && test -f "$rendered"
  cp "$rendered" "output/video/$scene.mp4"
done

cp gallery.py output/source/gallery.py
{
  echo "manim=$(manim --version)"
  echo "xelatex=$(xelatex --version | head -n 1)"
  echo "xcharter_text=$(fc-match XCharter | head -n 1)"
  echo "xcharter_math_file=/usr/local/share/fonts/figurize/XCharter-Math.otf"
  echo "dvisvgm=$(dvisvgm --version | head -n 1)"
} > output/runtime-report.txt

python validate.py output
