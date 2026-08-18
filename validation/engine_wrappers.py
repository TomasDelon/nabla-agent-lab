from engine_runtime import FigurizeCompiledScene


class CompiledBaseScene(FigurizeCompiledScene):
    PLAN_PATH = "base.plan.json"


class CompiledPatchedScene(FigurizeCompiledScene):
    PLAN_PATH = "patched.plan.json"
