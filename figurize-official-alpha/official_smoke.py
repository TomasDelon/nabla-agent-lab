from __future__ import annotations

import numpy as np
from manim import Axes, Dot, MathTex, Scene, TexTemplate, VGroup
from manim.mobject.geometry.tips import StealthTip

PAPER = "#FAF9F5"
GRAPHITE = "#1A1A18"
BERTAULT_BLUE = "#758FB2"
BERTAULT_GREEN = "#7F927A"
BERTAULT_PURPLE = "#8C7896"
BERTAULT_WARM_RED = "#B45F4D"


def xcharter_template() -> TexTemplate:
    template = TexTemplate(tex_compiler="lualatex", output_format=".pdf")
    template.add_to_preamble(r"\usepackage{fontspec}")
    template.add_to_preamble(r"\usepackage{unicode-math}")
    template.add_to_preamble(r"\setmainfont{XCharter}")
    template.add_to_preamble(
        r"\setmathfont{XCharter-Math.otf}[Path=/usr/local/share/fonts/figurize/]"
    )
    return template


class FigurizeOfficialSmoke(Scene):
    """Official Manim CE smoke test for the Figurize visual contracts.

    The scene uses direct, same-colour labels and no editorial connector line
    or arrow. Signed area is green above the axis and warm red below it.
    """

    def construct(self):
        self.camera.background_color = PAPER
        template = xcharter_template()
        axes = Axes(
            x_range=[-2.4, 2.4, 1],
            y_range=[-3.2, 3.2, 1],
            x_length=9.2,
            y_length=5.3,
            tips=True,
            axis_config={
                "color": GRAPHITE,
                "stroke_width": 2.0,
                "include_ticks": True,
                "include_numbers": False,
                "tick_size": 0.055,
                "tip_shape": StealthTip,
            },
        ).shift(0.2 * np.array([0.0, -1.0, 0.0]))
        for axis in (axes.x_axis, axes.y_axis):
            if axis.has_tip():
                axis.get_tip().scale(0.55)

        function = lambda x: x**3 - 2 * x
        graph = axes.plot(
            function,
            x_range=[-2.05, 2.05],
            color=BERTAULT_BLUE,
            stroke_width=4.0,
        )
        sqrt2 = np.sqrt(2)
        signed_parts = [
            (-2.0, -sqrt2, BERTAULT_WARM_RED),
            (-sqrt2, 0.0, BERTAULT_GREEN),
            (0.0, sqrt2, BERTAULT_WARM_RED),
            (sqrt2, 2.0, BERTAULT_GREEN),
        ]
        areas = VGroup(
            *[
                axes.get_area(
                    graph,
                    x_range=[left, right],
                    color=color,
                    opacity=0.34,
                )
                for left, right, color in signed_parts
            ]
        )
        roots = VGroup(
            *[
                Dot(axes.c2p(value, 0), radius=0.065, color=BERTAULT_BLUE)
                for value in (-sqrt2, 0.0, sqrt2)
            ]
        )

        tangent_x = 1.0
        tangent_y = function(tangent_x)
        tangent_slope = 3 * tangent_x**2 - 2
        tangent = axes.plot(
            lambda x: tangent_y + tangent_slope * (x - tangent_x),
            x_range=[0.55, 1.55],
            color=BERTAULT_PURPLE,
            stroke_width=3.0,
        )
        tangent_point = Dot(
            axes.c2p(tangent_x, tangent_y),
            radius=0.065,
            color=BERTAULT_PURPLE,
        )

        title = MathTex(
            r"f(x)=x^3-2x",
            tex_template=template,
            font_size=42,
            color=GRAPHITE,
        ).to_edge(np.array([0.0, 1.0, 0.0]), buff=0.28)
        curve_label = MathTex(
            r"f",
            tex_template=template,
            font_size=34,
            color=BERTAULT_BLUE,
        ).move_to(axes.c2p(1.82, function(1.82)) + np.array([0.26, 0.12, 0.0]))
        positive_label = MathTex(
            r"\mathcal A^{+}",
            tex_template=template,
            font_size=31,
            color=BERTAULT_GREEN,
        ).move_to(axes.c2p(-0.72, 0.72))
        negative_label = MathTex(
            r"\mathcal A^{-}",
            tex_template=template,
            font_size=31,
            color=BERTAULT_WARM_RED,
        ).move_to(axes.c2p(0.72, -0.72))
        tangent_label = MathTex(
            r"T_1",
            tex_template=template,
            font_size=30,
            color=BERTAULT_PURPLE,
        ).move_to(
            axes.c2p(1.48, tangent_y + tangent_slope * 0.48)
            + np.array([0.20, 0.12, 0.0])
        )

        self.add(
            areas,
            axes,
            graph,
            roots,
            tangent,
            tangent_point,
            title,
            curve_label,
            positive_label,
            negative_label,
            tangent_label,
        )
