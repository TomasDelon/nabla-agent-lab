from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def compile_scene_spec(spec: dict) -> dict:
    if spec.get("version") != "1.0":
        raise ValueError("Unsupported Scene Spec version")
    if spec.get("recipe") != "function.signed_area":
        raise ValueError("This render proof compiles function.signed_area only")
    expression = spec["input"]["expression"].replace(" ", "")
    if expression != "x**3-2*x":
        raise ValueError("The proof input must be x**3 - 2*x")
    a, b = map(float, spec["input"]["bounds"])
    root = math.sqrt(2.0)
    roots = [-root, 0.0, root]
    cuts = [a] + [value for value in roots if a < value < b] + [b]
    segments = []
    for left, right in zip(cuts[:-1], cuts[1:]):
        midpoint = (left + right) / 2.0
        value = midpoint**3 - 2.0 * midpoint
        segments.append(
            {
                "left": left,
                "right": right,
                "role": "positive" if value >= 0 else "negative",
            }
        )
    return {
        "engine_version": "1.0.0",
        "scene_id": spec["scene_id"],
        "recipe": spec["recipe"],
        "expression": expression,
        "viewport": spec["viewport"],
        "roots": roots,
        "signed_segments": segments,
        "components": [
            {"id": "axes", "type": "axes_2d", "role": "structure"},
            {"id": "area", "type": "signed_area", "role": "signed"},
            {"id": "function", "type": "function_curve", "role": "primary", "label": "f"},
            {"id": "roots", "type": "root_markers", "role": "primary"},
        ],
        "transparent_export": bool(spec.get("export", {}).get("transparent", True)),
    }


def apply_patch(plan: dict, patch: dict) -> dict:
    result = json.loads(json.dumps(plan))
    ids = {component["id"] for component in result["components"]}
    for operation in patch["operations"]:
        if operation["op"] != "add_component":
            raise ValueError("Only add_component is supported by this proof")
        component = operation["component"]
        if component["id"] in ids:
            raise ValueError("Duplicate component ID")
        result["components"].append(component)
        ids.add(component["id"])
    result["scene_id"] = patch["result_scene_id"]
    result["parent_scene_id"] = plan["scene_id"]
    result["patch_id"] = patch["patch_id"]
    return result


def main() -> None:
    spec = json.loads((ROOT / "scene_spec.json").read_text(encoding="utf-8"))
    patch = json.loads((ROOT / "scene_patch.json").read_text(encoding="utf-8"))
    base = compile_scene_spec(spec)
    patched = apply_patch(base, patch)
    (ROOT / "base.plan.json").write_text(json.dumps(base, indent=2), encoding="utf-8")
    (ROOT / "patched.plan.json").write_text(json.dumps(patched, indent=2), encoding="utf-8")
    print("Compiled base and patched render plans")


if __name__ == "__main__":
    main()
