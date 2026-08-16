from __future__ import annotations

import numpy as np
from manim import (
    Arrow,
    Axes,
    Create,
    DashedLine,
    Dot,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    Line,
    MathTex,
    PI,
    RIGHT,
    Text,
    UP,
    VGroup,
    ValueTracker,
    Write,
    always_redraw,
    linear,
    TracedPath,
)

from components import FigurizeScene, make_axes_2d, math_title, point_marker, title_group
from theme import (
    ATTENTION_PRIMARY,
    AXIS_PRIMARY,
    CONSTRUCTION_AUXILIARY,
    DURATION_EXPLANATORY,
    DURATION_NORMAL,
    FUNCTION_PRIMARY,
    POINT_CRITICAL,
    POINT_HIGHLIGHT,
    PROJECTION_GUIDE,
    STROKE_EMPHASIZED,
    STROKE_NORMAL,
    STROKE_STRONG,
    STROKE_THIN,
    TANGENT_PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    VECTOR_HIGHLIGHT,
)


class FunctionProgressiveAnimation(FigurizeScene):
    def construct(self):
        heading = math_title(
            r"f(x)=x^3-2x+1",
            "The scene is enriched without discarding previous components.",
        ).to_edge(UP, buff=0.25)
        axes = make_axes_2d((-3, 3, 1), (-5, 7, 1), x_length=8.7, y_length=5.05)
        axes.next_to(heading, DOWN, buff=0.3)
        curve = axes.plot(
            lambda x: x**3 - 2 * x + 1,
            x_range=[-2.25, 2.25],
            color=FUNCTION_PRIMARY,
            stroke_width=STROKE_STRONG,
        )

        def phase_label(text: str) -> Text:
            label = Text(text, font_size=22, color=TEXT_SECONDARY)
            label.to_edge(DOWN, buff=0.23)
            return label

        phase_1 = phase_label("1. Plot the function")
        self.play(FadeIn(heading, shift=UP * 0.12), FadeIn(axes), run_time=DURATION_NORMAL)
        self.play(Create(curve), Write(phase_1), run_time=DURATION_EXPLANATORY)
        self.wait(0.35)

        roots = [(-1 - np.sqrt(5)) / 2, (-1 + np.sqrt(5)) / 2, 1.0]
        root_markers = VGroup(*[point_marker(axes.c2p(root, 0), "highlight") for root in roots])
        root_specs = [
            (roots[0], r"\frac{-1-\sqrt5}{2}", DOWN + LEFT),
            (roots[1], r"\frac{-1+\sqrt5}{2}", DOWN + LEFT),
            (roots[2], "1", DOWN + RIGHT),
        ]
        root_labels = VGroup()
        for value, label, direction in root_specs:
            mob = MathTex(label, font_size=19, color=TEXT_SECONDARY)
            mob.next_to(axes.c2p(value, 0), direction, buff=0.17)
            root_labels.add(mob)
        phase_2 = phase_label("2. Highlight the roots")
        self.play(
            FadeOut(phase_1),
            FadeIn(phase_2),
            FadeIn(root_markers, scale=0.55),
            FadeIn(root_labels),
            run_time=DURATION_NORMAL,
        )
        self.wait(0.4)

        critical_x = [-np.sqrt(2 / 3), np.sqrt(2 / 3)]
        critical_group = VGroup()
        tangents = VGroup()
        for x_value in critical_x:
            y_value = x_value**3 - 2 * x_value + 1
            critical_group.add(point_marker(axes.c2p(x_value, y_value), "critical"))
            tangents.add(
                Line(
                    axes.c2p(x_value - 0.72, y_value),
                    axes.c2p(x_value + 0.72, y_value),
                    color=TANGENT_PRIMARY,
                    stroke_width=STROKE_EMPHASIZED,
                )
            )
        phase_3 = phase_label("3. Add horizontal tangents where f'(x)=0")
        self.play(
            FadeOut(phase_2),
            FadeIn(phase_3),
            FadeIn(critical_group, scale=0.55),
            run_time=DURATION_NORMAL,
        )
        self.play(*[Create(tangent) for tangent in tangents], run_time=DURATION_EXPLANATORY)
        self.wait(0.8)


class ProjectileMotionAnimation(FigurizeScene):
    def construct(self):
        v0 = 12.0
        angle = 50 * PI / 180
        g = 9.81
        vx = v0 * np.cos(angle)
        vy = v0 * np.sin(angle)
        t_apex = vy / g
        t_flight = 2 * vy / g
        x_impact = vx * t_flight
        y_apex = vy * t_apex - 0.5 * g * t_apex**2

        heading = title_group(
            "Projectile motion",
            "Trajectory, velocity, apex and impact are composed from one physical sketch.",
        ).to_edge(UP, buff=0.25)
        axes = Axes(
            x_range=[0, max(12, x_impact + 1), 2],
            y_range=[-1, max(6, y_apex + 1), 1],
            x_length=10.0,
            y_length=5.0,
            tips=True,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.8},
        )
        axes.next_to(heading, DOWN, buff=0.23)
        path_fn = lambda time: np.array(
            [vx * time, vy * time - 0.5 * g * time**2, 0.0]
        )
        full_path = axes.plot_parametric_curve(
            lambda time: (vx * time, vy * time - 0.5 * g * time**2),
            t_range=[0, t_flight],
            color=FUNCTION_PRIMARY,
            stroke_width=STROKE_NORMAL,
            stroke_opacity=0.32,
        )
        ground = Line(
            axes.c2p(0, 0),
            axes.c2p(max(12, x_impact + 1), 0),
            color=CONSTRUCTION_AUXILIARY,
            stroke_width=STROKE_NORMAL,
        )
        time = ValueTracker(0)
        projectile = always_redraw(
            lambda: Dot(
                axes.c2p(*path_fn(time.get_value())[:2]),
                radius=0.085,
                color=POINT_HIGHLIGHT,
            )
        )
        velocity = always_redraw(
            lambda: Arrow(
                projectile.get_center(),
                projectile.get_center()
                + np.array([vx, vy - g * time.get_value(), 0.0]) * 0.055,
                buff=0,
                color=VECTOR_HIGHLIGHT,
                stroke_width=STROKE_EMPHASIZED,
                max_tip_length_to_length_ratio=0.2,
            )
        )
        trail = TracedPath(
            projectile.get_center,
            stroke_color=FUNCTION_PRIMARY,
            stroke_width=STROKE_STRONG,
            dissipating_time=None,
        )
        gravity = Arrow(
            axes.c2p(1.0, 4.4),
            axes.c2p(1.0, 3.25),
            buff=0,
            color=ATTENTION_PRIMARY,
            stroke_width=STROKE_EMPHASIZED,
        )
        gravity_label = MathTex(r"\vec g", font_size=25, color=ATTENTION_PRIMARY).next_to(
            gravity, LEFT, buff=0.1
        )
        apex_point = point_marker(axes.c2p(vx * t_apex, y_apex), "critical")
        apex_label = MathTex(r"h_{\max}", font_size=25, color=POINT_CRITICAL).next_to(
            apex_point, UP, buff=0.14
        )
        apex_guide = DashedLine(
            axes.c2p(vx * t_apex, 0),
            axes.c2p(vx * t_apex, y_apex),
            color=PROJECTION_GUIDE,
            stroke_width=STROKE_THIN,
        )
        impact_point = point_marker(axes.c2p(x_impact, 0), "highlight")
        impact_label = Text("impact", font_size=22, color=TEXT_SECONDARY).next_to(
            impact_point, UP + LEFT, buff=0.14
        )
        parameters = MathTex(
            r"v_0=12\,\mathrm{m/s},\quad \theta=50^\circ,\quad g=9.81\,\mathrm{m/s^2}",
            font_size=24,
            color=TEXT_PRIMARY,
        ).to_edge(DOWN, buff=0.16)

        self.play(
            FadeIn(heading),
            FadeIn(axes),
            FadeIn(ground),
            Create(full_path),
            FadeIn(gravity),
            FadeIn(gravity_label),
            FadeIn(parameters),
            run_time=DURATION_NORMAL,
        )
        self.add(trail, projectile, velocity)
        self.play(time.animate.set_value(t_apex), run_time=2.2, rate_func=linear)
        self.play(
            FadeIn(apex_guide),
            FadeIn(apex_point, scale=0.6),
            FadeIn(apex_label),
            run_time=DURATION_NORMAL,
        )
        self.play(time.animate.set_value(t_flight), run_time=2.2, rate_func=linear)
        self.play(
            FadeIn(impact_point, scale=0.6),
            FadeIn(impact_label),
            run_time=DURATION_NORMAL,
        )
        self.wait(0.8)
