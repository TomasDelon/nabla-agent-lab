from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from manim import Axes, Circle, Dot, Line, MathTex, ThreeDScene, VGroup, UP, RIGHT, DOWN
from manim.mobject.geometry.tips import StealthTip

PAPER = "#FAF9F5"
GRAPHITE = "#1A1A18"
BLUE = "#758FB2"
GREEN = "#7F927A"
PURPLE = "#8C7896"
WARM_RED = "#B45F4D"


def xcharter_template():
    from manim import TexTemplate

    template = TexTemplate(tex_compiler="xelatex", output_format=".xdv")
    template.add_to_preamble(r"\usepackage{fontspec}")
    template.add_to_preamble(r"\usepackage{unicode-math}")
    template.add_to_preamble(r"\setmainfont{XCharter}")
    template.add_to_preamble(
        r"\setmathfont{XCharter-Math.otf}[Path=/usr/local/share/fonts/figurize/]"
    )
    return template


class FigurizeCompiledScene(ThreeDScene):
    PLAN_PATH: str = ""

    def construct(self):
        plan = json.loads(Path(self.PLAN_PATH).read_text(encoding="utf-8"))
        self.camera.background_color = PAPER
        template = xcharter_template()
        viewport = plan["viewport"]
        axes = Axes(
            x_range=[viewport["x_min"], viewport["x_max"], 1],
            y_range=[viewport["y_min"], viewport["y_max"], 1],
            x_length=10.0,
            y_length=5.5,
            tips=True,
            axis_config={
                "color": GRAPHITE,
                "stroke_width": 1.8,
                "include_ticks": True,
                "include_numbers": False,
                "tick_size": 0.05,
                "tip_shape": StealthTip,
            },
        )
        for axis in (axes.x_axis, axes.y_axis):
            if axis.has_tip():
                axis.get_tip().scale(0.52)

        function = lambda x: x**3 - 2 * x
        graph = axes.plot(
            function,
            x_range=[-2.05, 2.05],
            color=BLUE,
            stroke_width=4.0,
        )
        graph_for_area = axes.plot(function, x_range=[-2.05, 2.05])
        areas = VGroup()
        for segment in plan["signed_segments"]:
            color = GREEN if segment["role"] == "positive" else WARM_RED
            areas.add(
                axes.get_area(
                    graph_for_area,
                    x_range=[segment["left"], segment["right"]],
                    color=color,
                    opacity=0.34,
                )
            )
        roots = VGroup(
            *[Dot(axes.c2p(value, 0), radius=0.065, color=BLUE) for value in plan["roots"]]
        )
        title = MathTex(
            r"f(x)=x^3-2x",
            tex_template=template,
            font_size=38,
            color=GRAPHITE,
        ).to_edge(UP, buff=0.24)
        labels = VGroup(
            MathTex("f", tex_template=template, font_size=31, color=BLUE).move_to(
                axes.c2p(1.82, function(1.82)) + RIGHT * 0.17
            ),
            MathTex(
                r"\mathcal A^{+}",
                tex_template=template,
                font_size=30,
                color=GREEN,
            ).move_to(axes.c2p(-0.78, 0.72)),
            MathTex(
                r"\mathcal A^{-}",
                tex_template=template,
                font_size=30,
                color=WARM_RED,
            ).move_to(axes.c2p(0.78, -0.72)),
        )
        self.add(areas, axes, graph, roots, title, labels)

        component_types = {component["type"] for component in plan["components"]}
        if "tangent_line" in component_types:
            tangent_component = next(
                component
                for component in plan["components"]
                if component["type"] == "tangent_line"
            )
            x0 = float(tangent_component["payload"]["at_x"])
            span = float(tangent_component["payload"].get("span", 1.6))
            y0 = function(x0)
            slope = 3 * x0**2 - 2
            half = span / 2
            tangent = Line(
                axes.c2p(x0 - half, y0 - slope * half),
                axes.c2p(x0 + half, y0 + slope * half),
                color=PURPLE,
                stroke_width=2.8,
            )
            point = Dot(axes.c2p(x0, y0), radius=0.065, color=PURPLE)
            tangent_label = MathTex(
                tangent_component.get("label", "T"),
                tex_template=template,
                font_size=28,
                color=PURPLE,
            ).move_to(tangent.get_right() + UP * 0.18)
            self.add(tangent, point, tangent_label)
