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

rm -rf output_v2 media_v2
mkdir -p output_v2/static output_v2/video output_v2/logs output_v2/source

python compile_spec.py > output_v2/logs/compile.log 2>&1

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
  echo "Rendering direct Manim reference $scene"
  manim -ql -s --format=png --transparent --disable_caching \
    --media_dir media_v2 \
    -o "$scene" \
    gallery.py "$scene" \
    >"output_v2/logs/$scene.log" 2>&1
  rendered=$(find media_v2 -type f -name "$scene*.png" | sort | tail -n 1)
  test -n "$rendered" && test -f "$rendered"
  cp "$rendered" "output_v2/static/$scene.png"
done

COMPILED_SCENES=(CompiledBaseScene CompiledPatchedScene)
for scene in "${COMPILED_SCENES[@]}"; do
  echo "Rendering compiled engine scene $scene"
  manim -ql -s --format=png --transparent --disable_caching \
    --media_dir media_v2 \
    -o "$scene" \
    engine_wrappers.py "$scene" \
    >"output_v2/logs/$scene.log" 2>&1
  rendered=$(find media_v2 -type f -name "$scene*.png" | sort | tail -n 1)
  test -n "$rendered" && test -f "$rendered"
  cp "$rendered" "output_v2/static/$scene.png"
done

ANIMATIONS=(LinearTransformAnimationScene SignedAreaAnimationScene)
for scene in "${ANIMATIONS[@]}"; do
  echo "Rendering animation $scene"
  manim -ql --disable_caching \
    --media_dir media_v2 \
    -o "$scene" \
    gallery.py "$scene" \
    >"output_v2/logs/$scene.log" 2>&1
  rendered=$(find media_v2 -type f -name "$scene*.mp4" | sort | tail -n 1)
  test -n "$rendered" && test -f "$rendered"
  cp "$rendered" "output_v2/video/$scene.mp4"
done

cp gallery.py output_v2/source/gallery.py
cp engine_runtime.py output_v2/source/engine_runtime.py
cp engine_wrappers.py output_v2/source/engine_wrappers.py
cp compile_spec.py output_v2/source/compile_spec.py
cp scene_spec.json output_v2/source/scene_spec.json
cp scene_patch.json output_v2/source/scene_patch.json
cp base.plan.json output_v2/source/base.plan.json
cp patched.plan.json output_v2/source/patched.plan.json

{
  echo "manim=$(manim --version)"
  echo "xelatex=$(xelatex --version | head -n 1)"
  echo "xcharter_text=$(fc-match XCharter | head -n 1)"
  echo "xcharter_math_file=/usr/local/share/fonts/figurize/XCharter-Math.otf"
  echo "dvisvgm=$(dvisvgm --version | head -n 1)"
} > output_v2/runtime-report.txt

python validate_v2.py output_v2
