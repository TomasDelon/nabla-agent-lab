from __future__ import annotations

import numpy as np
from manim import (
    ApplyMatrix,
    Arrow,
    Axes,
    Circle,
    Create,
    DashedLine,
    Dot,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    Line,
    MathTex,
    NumberPlane,
    ORIGIN,
    PI,
    RIGHT,
    TAU,
    Text,
    TracedPath,
    UP,
    VGroup,
    ValueTracker,
    Write,
    always_redraw,
    linear,
)

from components import FigurizeScene, make_axes_2d, math_title, point_marker, title_group
from theme import (
    ATTENTION_PRIMARY,
    AXIS_PRIMARY,
    CONSTRUCTION_AUXILIARY,
    DURATION_EXPLANATORY,
    DURATION_NORMAL,
    DURATION_TRANSFORM,
    FUNCTION_PRIMARY,
    FUNCTION_SECONDARY,
    GRID_MAJOR,
    POINT_CRITICAL,
    POINT_HIGHLIGHT,
    PROJECTION_GUIDE,
    REGION_PRIMARY,
    STROKE_EMPHASIZED,
    STROKE_NORMAL,
    STROKE_STRONG,
    STROKE_THIN,
    TANGENT_PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    VECTOR_DEFAULT,
    VECTOR_HIGHLIGHT,
)


class FunctionProgressiveAnimation(FigurizeScene):
    """The canonical edit sequence: plot, roots, critical points and tangents."""

    def construct(self):
        heading = math_title(
            r"f(x)=x^3-2x+1",
            "The scene is enriched without discarding previous components.",
        ).to_edge(UP, buff=0.25)
        axes = make_axes_2d((-3, 3, 1), (-5, 7, 1), x_length=8.8, y_length=5.15)
        axes.next_to(heading, DOWN, buff=0.28)
        curve = axes.plot(
            lambda x: x**3 - 2 * x + 1,
            x_range=[-2.25, 2.25],
            color=FUNCTION_PRIMARY,
            stroke_width=STROKE_STRONG,
        )
        phase = Text("1. Plot the function", font_size=24, color=TEXT_SECONDARY).to_corner(DOWN + LEFT, buff=0.35)

        self.play(FadeIn(heading, shift=UP * 0.12), FadeIn(axes), run_time=DURATION_NORMAL)
        self.play(Create(curve), Write(phase), run_time=DURATION_EXPLANATORY)
        self.wait(0.35)

        roots = [(-1 - np.sqrt(5)) / 2, (-1 + np.sqrt(5)) / 2, 1.0]
        root_markers = VGroup(*[point_marker(axes.c2p(root, 0), "highlight") for root in roots])
        root_labels = VGroup(*[
            MathTex(label, font_size=20, color=TEXT_SECONDARY).next_to(
                axes.c2p(root, 0), DOWN, buff=0.13
            )
            for root, label in zip(
                roots,
                [r"\frac{-1-\sqrt5}{2}", r"\frac{-1+\sqrt5}{2}", "1"],
            )
        ])
        phase_2 = Text("2. Highlight the roots", font_size=24, color=TEXT_SECONDARY).move_to(phase)
        self.play(FadeOut(phase), FadeIn(phase_2), FadeIn(root_markers, scale=0.55), FadeIn(root_labels), run_time=DURATION_NORMAL)
        self.wait(0.4)

        critical_x = [-np.sqrt(2 / 3), np.sqrt(2 / 3)]
        critical_group = VGroup()
        tangents = VGroup()
        for x_value in critical_x:
            y_value = x_value**3 - 2 * x_value + 1
            critical_group.add(point_marker(axes.c2p(x_value, y_value), "critical"))
            tangents.add(
                Line(
                    axes.c2p(x_value - 0.75, y_value),
                    axes.c2p(x_value + 0.75, y_value),
                    color=TANGENT_PRIMARY,
                    stroke_width=STROKE_EMPHASIZED,
                )
            )
        phase_3 = Text("3. Add horizontal tangents where f'(x)=0", font_size=24, color=TEXT_SECONDARY).move_to(phase)
        self.play(FadeOut(phase_2), FadeIn(phase_3), FadeIn(critical_group, scale=0.55), run_time=DURATION_NORMAL)
        self.play(*[Create(tangent) for tangent in tangents], run_time=DURATION_EXPLANATORY)
        self.wait(0.8)


class LinearTransformationAnimation(FigurizeScene):
    def construct(self):
        heading = math_title(
            r"A=\begin{pmatrix}1&0.85\\0.25&1\end{pmatrix}",
            "A matrix acts on the grid and on the basis vectors simultaneously.",
        ).to_edge(UP, buff=0.25)
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            x_length=9.2,
            y_length=5.2,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.8},
            background_line_style={
                "stroke_color": GRID_MAJOR,
                "stroke_width": 1.0,
                "stroke_opacity": 0.42,
            },
        )
        plane.next_to(heading, DOWN, buff=0.3)
        origin = plane.c2p(0, 0)
        e1 = Arrow(origin, plane.c2p(1, 0), buff=0, color=VECTOR_HIGHLIGHT, stroke_width=STROKE_EMPHASIZED)
        e2 = Arrow(origin, plane.c2p(0, 1), buff=0, color=TANGENT_PRIMARY, stroke_width=STROKE_EMPHASIZED)
        labels = VGroup(
            MathTex(r"e_1", font_size=24, color=VECTOR_HIGHLIGHT).next_to(e1.get_end(), RIGHT, buff=0.1),
            MathTex(r"e_2", font_size=24, color=TANGENT_PRIMARY).next_to(e2.get_end(), UP, buff=0.1),
        )
        matrix = [[1.0, 0.85], [0.25, 1.0]]
        self.play(FadeIn(heading), FadeIn(plane), FadeIn(e1), FadeIn(e2), FadeIn(labels), run_time=DURATION_NORMAL)
        self.wait(0.35)
        self.play(
            ApplyMatrix(matrix, plane),
            ApplyMatrix(matrix, e1),
            ApplyMatrix(matrix, e2),
            FadeOut(labels),
            run_time=2.4,
        )
        transformed_labels = VGroup(
            MathTex(r"Ae_1", font_size=24, color=VECTOR_HIGHLIGHT).next_to(e1.get_end(), RIGHT, buff=0.1),
            MathTex(r"Ae_2", font_size=24, color=TANGENT_PRIMARY).next_to(e2.get_end(), UP, buff=0.1),
        )
        self.play(FadeIn(transformed_labels), run_time=DURATION_NORMAL)
        self.wait(0.8)


class SineFromCircleAnimation(FigurizeScene):
    def construct(self):
        heading = math_title(
            r"(\cos t,\sin t)",
            "The vertical coordinate of a rotating point constructs y=sin(t).",
        ).to_edge(UP, buff=0.23)
        center = LEFT * 3.7 + DOWN * 0.45
        radius = 1.65
        circle = Circle(radius=radius, color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED).move_to(center)
        circle_axes = VGroup(
            Line(center + LEFT * 1.95, center + RIGHT * 1.95, color=AXIS_PRIMARY, stroke_width=STROKE_THIN),
            Line(center + DOWN * 1.95, center + UP * 1.95, color=AXIS_PRIMARY, stroke_width=STROKE_THIN),
        )
        axes = Axes(
            x_range=[0, TAU, PI / 2],
            y_range=[-1.3, 1.3, 0.5],
            x_length=6.0,
            y_length=3.7,
            tips=False,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.8},
        ).shift(RIGHT * 2.8 + DOWN * 0.45)
        theta = ValueTracker(0)
        circle_dot = always_redraw(
            lambda: Dot(
                center + radius * np.array([np.cos(theta.get_value()), np.sin(theta.get_value()), 0]),
                radius=0.075,
                color=POINT_HIGHLIGHT,
            )
        )
        radius_line = always_redraw(
            lambda: Line(center, circle_dot.get_center(), color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_NORMAL)
        )
        graph_dot = always_redraw(
            lambda: Dot(
                axes.c2p(theta.get_value(), np.sin(theta.get_value())),
                radius=0.07,
                color=POINT_HIGHLIGHT,
            )
        )
        connector = always_redraw(
            lambda: DashedLine(
                circle_dot.get_center(),
                graph_dot.get_center(),
                dash_length=0.08,
                color=PROJECTION_GUIDE,
                stroke_width=STROKE_THIN,
            )
        )
        trail = TracedPath(
            graph_dot.get_center,
            stroke_color=FUNCTION_SECONDARY,
            stroke_width=STROKE_STRONG,
            dissipating_time=None,
        )
        self.play(FadeIn(heading), FadeIn(circle_axes), Create(circle), FadeIn(axes), run_time=DURATION_NORMAL)
        self.add(trail, radius_line, connector, circle_dot, graph_dot)
        self.play(theta.animate.set_value(TAU), run_time=4.5, rate_func=linear)
        self.wait(0.7)


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
            y_range=[0, max(6, y_apex + 1), 1],
            x_length=10.0,
            y_length=4.8,
            tips=True,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.8},
        )
        axes.next_to(heading, DOWN, buff=0.28)
        path_fn = lambda time: np.array([
            vx * time,
            vy * time - 0.5 * g * time**2,
            0.0,
        ])
        full_path = axes.plot_parametric_curve(
            lambda time: (vx * time, vy * time - 0.5 * g * time**2),
            t_range=[0, t_flight],
            color=FUNCTION_PRIMARY,
            stroke_width=STROKE_NORMAL,
            stroke_opacity=0.32,
        )
        ground = Line(axes.c2p(0, 0), axes.c2p(max(12, x_impact + 1), 0), color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_NORMAL)
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
                + np.array([
                    vx,
                    vy - g * time.get_value(),
                    0.0,
                ])
                * 0.085,
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
        gravity_label = MathTex(r"\vec g", font_size=25, color=ATTENTION_PRIMARY).next_to(gravity, LEFT, buff=0.1)
        apex_point = point_marker(axes.c2p(vx * t_apex, y_apex), "critical")
        apex_label = MathTex(r"h_{\max}", font_size=25, color=POINT_CRITICAL).next_to(apex_point, UP, buff=0.14)
        apex_guide = DashedLine(
            axes.c2p(vx * t_apex, 0),
            axes.c2p(vx * t_apex, y_apex),
            color=PROJECTION_GUIDE,
            stroke_width=STROKE_THIN,
        )
        impact_point = point_marker(axes.c2p(x_impact, 0), "highlight")
        impact_label = Text("impact", font_size=22, color=TEXT_SECONDARY).next_to(impact_point, UP + LEFT, buff=0.14)
        parameters = MathTex(
            r"v_0=12\,\mathrm{m/s},\quad \theta=50^\circ,\quad g=9.81\,\mathrm{m/s^2}",
            font_size=24,
            color=TEXT_PRIMARY,
        ).to_edge(DOWN, buff=0.18)

        self.play(FadeIn(heading), FadeIn(axes), FadeIn(ground), Create(full_path), FadeIn(gravity), FadeIn(gravity_label), FadeIn(parameters), run_time=DURATION_NORMAL)
        self.add(trail, projectile, velocity)
        self.play(time.animate.set_value(t_apex), run_time=2.2, rate_func=linear)
        self.play(FadeIn(apex_guide), FadeIn(apex_point, scale=0.6), FadeIn(apex_label), run_time=DURATION_NORMAL)
        self.play(time.animate.set_value(t_flight), run_time=2.2, rate_func=linear)
        self.play(FadeIn(impact_point, scale=0.6), FadeIn(impact_label), run_time=DURATION_NORMAL)
        self.wait(0.8)
