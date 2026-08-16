#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MEDIA="$ROOT/media"
OUTPUT="$ROOT/output"
LOGS="$OUTPUT/logs"

rm -rf "$MEDIA" "$OUTPUT"
mkdir -p "$OUTPUT/static" "$OUTPUT/transparent" "$OUTPUT/video" "$OUTPUT/gif" "$LOGS"

STATIC_2D=(
  PrimitiveComponents
  AxisTicksGrid
  IntervalComponents
  CartesianComponents
  GeometryComponents
  FunctionBasic
  FunctionEvaluation
  FunctionRootsTangents
  ArbitraryPointOnCurve
  AreaUnderCurve
  AlgebraAreaIdentity
  UnitCircleCosEquation
  ProbabilityNormalRegion
  ScatterRegression
  VectorFieldComposition
  LinearTransformationStatic
  DarkBackgroundPreview
)

STATIC_3D=(
  PointVectorSpace3D
  SolidGeometryCodes3D
  SurfaceContours3D
  TangentPlaneSurface3D
)

TRANSPARENT_SCENES=(
  PrimitiveComponents
  IntervalComponents
  GeometryComponents
  FunctionRootsTangents
  ArbitraryPointOnCurve
  ProbabilityNormalRegion
  TangentPlaneSurface3D
)

ANIMATIONS=(
  FunctionProgressiveAnimation
  LinearTransformationAnimation
  SineFromCircleAnimation
  ProjectileMotionAnimation
)

find_output() {
  local extension="$1"
  local pattern="$2"
  find "$MEDIA" -type f -name "${pattern}*.${extension}" -print | sort | tail -n 1
}

render_static() {
  local file="$1"
  local scene="$2"
  local output_name="${scene}_static"
  echo "[static] $scene"
  manim \
    -ql \
    -s \
    --format=png \
    --disable_caching \
    --media_dir "$MEDIA" \
    -o "$output_name" \
    "$file" "$scene" \
    >"$LOGS/${scene}.log" 2>&1
  local rendered
  rendered="$(find_output png "$output_name")"
  if [[ -z "$rendered" || ! -f "$rendered" ]]; then
    echo "Missing PNG for $scene" >&2
    cat "$LOGS/${scene}.log" >&2
    exit 1
  fi
  cp "$rendered" "$OUTPUT/static/${scene}.png"
}

render_transparent() {
  local file="$1"
  local scene="$2"
  local output_name="${scene}_transparent"
  echo "[transparent] $scene"
  manim \
    -ql \
    -s \
    --format=png \
    --transparent \
    --disable_caching \
    --media_dir "$MEDIA" \
    -o "$output_name" \
    "$file" "$scene" \
    >"$LOGS/${scene}_transparent.log" 2>&1
  local rendered
  rendered="$(find_output png "$output_name")"
  if [[ -z "$rendered" || ! -f "$rendered" ]]; then
    echo "Missing transparent PNG for $scene" >&2
    cat "$LOGS/${scene}_transparent.log" >&2
    exit 1
  fi
  cp "$rendered" "$OUTPUT/transparent/${scene}.png"
}

render_animation() {
  local scene="$1"
  local output_name="${scene}_video"
  echo "[animation] $scene"
  manim \
    -ql \
    --disable_caching \
    --media_dir "$MEDIA" \
    -o "$output_name" \
    animations.py "$scene" \
    >"$LOGS/${scene}.log" 2>&1
  local rendered
  rendered="$(find_output mp4 "$output_name")"
  if [[ -z "$rendered" || ! -f "$rendered" ]]; then
    echo "Missing MP4 for $scene" >&2
    cat "$LOGS/${scene}.log" >&2
    exit 1
  fi
  cp "$rendered" "$OUTPUT/video/${scene}.mp4"
}

for scene in "${STATIC_2D[@]}"; do
  render_static gallery_2d.py "$scene"
done

for scene in "${STATIC_3D[@]}"; do
  render_static gallery_3d.py "$scene"
done

for scene in "${TRANSPARENT_SCENES[@]}"; do
  if [[ "$scene" == *"3D" ]]; then
    render_transparent gallery_3d.py "$scene"
  else
    render_transparent gallery_2d.py "$scene"
  fi
done

for scene in "${ANIMATIONS[@]}"; do
  render_animation "$scene"
done

python - <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path

root = Path("output")
files = []
for path in sorted(p for p in root.rglob("*") if p.is_file() and "logs" not in p.parts):
    files.append(
        {
            "path": path.as_posix(),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
manifest = {
    "renderer": "Manim Community v0.20.1",
    "static_count": len(list((root / "static").glob("*.png"))),
    "transparent_count": len(list((root / "transparent").glob("*.png"))),
    "video_count": len(list((root / "video").glob("*.mp4"))),
    "files": files,
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))
PY

expected_static=$((${#STATIC_2D[@]} + ${#STATIC_3D[@]}))
actual_static=$(find "$OUTPUT/static" -maxdepth 1 -type f -name '*.png' | wc -l)
actual_transparent=$(find "$OUTPUT/transparent" -maxdepth 1 -type f -name '*.png' | wc -l)
actual_video=$(find "$OUTPUT/video" -maxdepth 1 -type f -name '*.mp4' | wc -l)

[[ "$actual_static" -eq "$expected_static" ]]
[[ "$actual_transparent" -eq "${#TRANSPARENT_SCENES[@]}" ]]
[[ "$actual_video" -eq "${#ANIMATIONS[@]}" ]]

echo "Rendered $actual_static static PNGs, $actual_transparent transparent PNGs and $actual_video MP4s."
