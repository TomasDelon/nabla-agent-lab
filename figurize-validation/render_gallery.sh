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
  AxisTicksGrid
  IntervalComponents
  GeometryComponents
  FunctionBasic
  FunctionEvaluation
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

STATIC_REFINED=(
  PrimitiveComponents
  CartesianComponents
  FunctionRootsTangents
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
  echo "[static] $scene from $file"
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
  echo "[transparent] $scene from $file"
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
  local file="$1"
  local scene="$2"
  local output_name="${scene}_video"
  echo "[animation] $scene from $file"
  manim \
    -ql \
    --disable_caching \
    --media_dir "$MEDIA" \
    -o "$output_name" \
    "$file" "$scene" \
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

static_file_for_scene() {
  case "$1" in
    PrimitiveComponents|CartesianComponents|FunctionRootsTangents|PointVectorSpace3D|SolidGeometryCodes3D|SurfaceContours3D|TangentPlaneSurface3D)
      echo "gallery_refined.py"
      ;;
    *)
      echo "gallery_2d.py"
      ;;
  esac
}

transparent_file_for_scene() {
  case "$1" in
    PrimitiveComponents|FunctionRootsTangents|TangentPlaneSurface3D)
      echo "gallery_refined.py"
      ;;
    *)
      echo "gallery_2d.py"
      ;;
  esac
}

animation_file_for_scene() {
  case "$1" in
    FunctionProgressiveAnimation|ProjectileMotionAnimation)
      echo "animations_refined.py"
      ;;
    *)
      echo "animations.py"
      ;;
  esac
}

for scene in "${STATIC_2D[@]}"; do
  render_static gallery_2d.py "$scene"
done

for scene in "${STATIC_REFINED[@]}"; do
  render_static "$(static_file_for_scene "$scene")" "$scene"
done

for scene in "${TRANSPARENT_SCENES[@]}"; do
  render_transparent "$(transparent_file_for_scene "$scene")" "$scene"
done

for scene in "${ANIMATIONS[@]}"; do
  render_animation "$(animation_file_for_scene "$scene")" "$scene"
done

expected_static=$((${#STATIC_2D[@]} + ${#STATIC_REFINED[@]}))
actual_static=$(find "$OUTPUT/static" -maxdepth 1 -type f -name '*.png' | wc -l)
actual_transparent=$(find "$OUTPUT/transparent" -maxdepth 1 -type f -name '*.png' | wc -l)
actual_video=$(find "$OUTPUT/video" -maxdepth 1 -type f -name '*.mp4' | wc -l)

[[ "$actual_static" -eq "$expected_static" ]]
[[ "$actual_transparent" -eq "${#TRANSPARENT_SCENES[@]}" ]]
[[ "$actual_video" -eq "${#ANIMATIONS[@]}" ]]

echo "Manim rendered $actual_static static PNGs, $actual_transparent transparent PNGs and $actual_video MP4s."
