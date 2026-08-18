from __future__ import annotations

import math

import numpy as np
from manim import (
    Angle,
    ApplyMatrix,
    Arrow,
    Arrow3D,
    Axes,
    Circle,
    Create,
    DashedLine,
    Dot,
    Dot3D,
    DOWN,
    FadeIn,
    LEFT,
    Line,
    Line3D,
    MathTex,
    NumberLine,
    NumberPlane,
    ORIGIN,
    ParametricFunction,
    Polygon,
    Rectangle,
    RIGHT,
    Surface,
    TAU,
    Text,
    ThreeDAxes,
    ThreeDScene,
    UP,
    VGroup,
    ValueTracker,
    always_redraw,
    linear,
    DEGREES,
)
from manim.mobject.geometry.tips import StealthTip

PAPER = "#FAF9F5"
GRAPHITE = "#1A1A18"
GRAPHITE_MUTED = "#6A6862"
GRID = "#D8D5CC"
BLUE = "#758FB2"
BLUE_LIGHT = "#A8BAD0"
GREEN = "#7F927A"
GREEN_LIGHT = "#B7C2B3"
PURPLE = "#8C7896"
PURPLE_LIGHT = "#BBAFC1"
WARM_RED = "#B45F4D"
WARM_RED_LIGHT = "#D6A49A"


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


TEMPLATE = xcharter_template()


def math_label(text: str, color: str = GRAPHITE, size: int = 30):
    return MathTex(text, tex_template=TEMPLATE, font_size=size, color=color)


def text_label(text: str, color: str = GRAPHITE, size: int = 30):
    return MathTex(r"\text{" + text + "}", tex_template=TEMPLATE, font_size=size, color=color)


def small_axis_tips(axes) -> None:
    for axis in (axes.x_axis, axes.y_axis):
        if axis.has_tip():
            axis.get_tip().scale(0.52)


def small_axis_tips_3d(axes) -> None:
    for axis in (axes.x_axis, axes.y_axis, axes.z_axis):
        if axis.has_tip():
            axis.get_tip().scale(0.52)


def axes_2d(x_range=(-4, 4, 1), y_range=(-3, 3, 1), grid=False):
    cls = NumberPlane if grid else Axes
    kwargs = dict(
        x_range=x_range,
        y_range=y_range,
        x_length=10.0,
        y_length=5.5,
        axis_config={
            "color": GRAPHITE,
            "stroke_width": 1.8,
            "tip_shape": StealthTip,
            "tick_size": 0.05,
        },
    )
    if grid:
        kwargs["background_line_style"] = {
            "stroke_color": GRID,
            "stroke_width": 0.75,
            "stroke_opacity": 0.36,
        }
    axes = cls(**kwargs)
    small_axis_tips(axes)
    return axes


def title(text: str):
    return math_label(text, GRAPHITE, 38).to_edge(UP, buff=0.24)


def filled_point(point, color=BLUE, radius=0.065):
    return Dot(point, radius=radius, color=color)


def hollow_point(point, color=BLUE, radius=0.082):
    return Circle(radius=radius, color=color, stroke_width=2.3, fill_opacity=0).move_to(point)


class FigurizeBaseScene(ThreeDScene):
    def setup(self):
        super().setup()
        self.camera.background_color = PAPER


class SignedAreaScene(FigurizeBaseScene):
    def construct(self):
        axes = axes_2d((-2.5, 2.5, 1), (-3.4, 3.4, 1))
        f = lambda x: x**3 - 2 * x
        curve = axes.plot(f, x_range=[-2.05, 2.05], color=BLUE, stroke_width=4.0)
        root = math.sqrt(2)
        intervals = [
            (-2.0, -root, WARM_RED),
            (-root, 0.0, GREEN),
            (0.0, root, WARM_RED),
            (root, 2.0, GREEN),
        ]
        areas = VGroup(
            *[
                axes.get_area(curve, x_range=[left, right], color=color, opacity=0.34)
                for left, right, color in intervals
            ]
        )
        roots = VGroup(*[filled_point(axes.c2p(value, 0), BLUE) for value in (-root, 0, root)])
        labels = VGroup(
            math_label("f", BLUE, 31).move_to(axes.c2p(1.82, f(1.82)) + RIGHT * 0.17),
            math_label(r"\mathcal A^{+}", GREEN, 30).move_to(axes.c2p(-0.78, 0.72)),
            math_label(r"\mathcal A^{-}", WARM_RED, 30).move_to(axes.c2p(0.78, -0.72)),
        )
        self.add(areas, axes, curve, roots, title(r"f(x)=x^3-2x"), labels)


class FunctionRootsTangentsScene(FigurizeBaseScene):
    def construct(self):
        axes = axes_2d((-3, 3, 1), (-5, 7, 1))
        f = lambda x: x**3 - 2 * x + 1
        curve = axes.plot(f, x_range=[-2.25, 2.25], color=BLUE, stroke_width=4.0)
        roots_values = [(-1 - math.sqrt(5)) / 2, (-1 + math.sqrt(5)) / 2, 1.0]
        roots = VGroup(*[filled_point(axes.c2p(value, 0), BLUE) for value in roots_values])
        tangents = VGroup()
        critical_points = VGroup()
        for x0 in (-math.sqrt(2 / 3), math.sqrt(2 / 3)):
            y0 = f(x0)
            tangents.add(Line(axes.c2p(x0 - 0.72, y0), axes.c2p(x0 + 0.72, y0), color=PURPLE, stroke_width=2.8))
            critical_points.add(filled_point(axes.c2p(x0, y0), PURPLE))
        labels = VGroup(
            math_label("f", BLUE, 31).move_to(axes.c2p(1.92, f(1.92)) + LEFT * 0.13),
            math_label(r"T_1", PURPLE, 27).move_to(tangents[0].get_left() + UP * 0.2),
            math_label(r"T_2", PURPLE, 27).move_to(tangents[1].get_right() + DOWN * 0.2),
        )
        self.add(axes, curve, roots, tangents, critical_points, title(r"f(x)=x^3-2x+1"), labels)


class IntervalScene(FigurizeBaseScene):
    def construct(self):
        line = NumberLine(
            x_range=[-5, 6, 1],
            length=10.4,
            include_numbers=True,
            font_size=22,
            color=GRAPHITE,
            stroke_width=1.8,
            tip_shape=StealthTip,
        )
        if line.has_tip():
            line.get_tip().scale(0.52)
        first = Line(line.n2p(-3), line.n2p(1), color=BLUE, stroke_width=7)
        second = Line(line.n2p(2), line.n2p(5), color=PURPLE, stroke_width=7)
        markers = VGroup(
            hollow_point(line.n2p(-3), BLUE),
            filled_point(line.n2p(1), BLUE),
            filled_point(line.n2p(2), PURPLE),
            hollow_point(line.n2p(5), PURPLE),
        )
        labels = VGroup(
            math_label(r"(-3,1]", BLUE, 29).next_to(first, UP, buff=0.3),
            math_label(r"[2,5)", PURPLE, 29).next_to(second, DOWN, buff=0.3),
        )
        self.add(line, first, second, markers, title(r"(-3,1]\cup[2,5)"), labels)


class PointVectorScene(FigurizeBaseScene):
    def construct(self):
        plane = axes_2d((-4, 4, 1), (-3, 3, 1), grid=True)
        a = plane.c2p(2, 1.2)
        b = plane.c2p(-1.4, 2.0)
        point_a = filled_point(a, BLUE)
        point_b = hollow_point(b, PURPLE)
        guides = VGroup(
            DashedLine(plane.c2p(2, 0), a, color=GREEN, stroke_width=1.3),
            DashedLine(plane.c2p(0, 1.2), a, color=GREEN, stroke_width=1.3),
        )
        vector = Arrow(plane.c2p(0, 0), plane.c2p(2.8, 2), buff=0, color=BLUE, stroke_width=3.0, max_tip_length_to_length_ratio=0.16)
        labels = VGroup(
            math_label(r"A(2,1.2)", BLUE, 27).next_to(point_a, DOWN + RIGHT, buff=0.12),
            math_label(r"B(x,y)", PURPLE, 27).next_to(point_b, UP + LEFT, buff=0.12),
            math_label(r"\vec v", BLUE, 28).next_to(vector.get_end(), UP + RIGHT, buff=0.1),
        )
        self.add(plane, guides, point_a, point_b, vector, title(r"\text{Points, vector and projections}"), labels)


class TriangleScene(FigurizeBaseScene):
    def construct(self):
        a = np.array([-3.0, -1.8, 0.0])
        b = np.array([2.8, -1.8, 0.0])
        c = np.array([-0.8, 1.9, 0.0])
        triangle = Polygon(a, b, c, color=BLUE, stroke_width=3.0, fill_color=BLUE, fill_opacity=0.07)
        foot = np.array([c[0], a[1], 0.0])
        altitude = DashedLine(c, foot, color=GREEN, stroke_width=1.5)
        right_angle = VGroup(
            Line(foot, foot + RIGHT * 0.25, color=GREEN, stroke_width=1.4),
            Line(foot + RIGHT * 0.25, foot + RIGHT * 0.25 + UP * 0.25, color=GREEN, stroke_width=1.4),
        )
        angle = Angle(Line(a, b), Line(a, c), radius=0.48, color=PURPLE, stroke_width=2.0)
        points = VGroup(*[filled_point(point, GRAPHITE, 0.055) for point in (a, b, c)])
        labels = VGroup(
            math_label("A", GRAPHITE, 27).next_to(a, DOWN + LEFT, buff=0.1),
            math_label("B", GRAPHITE, 27).next_to(b, DOWN + RIGHT, buff=0.1),
            math_label("C", GRAPHITE, 27).next_to(c, UP, buff=0.1),
            math_label("h", GREEN, 27).next_to(altitude, RIGHT, buff=0.1),
            math_label(r"\alpha", PURPLE, 27).move_to(a + RIGHT * 0.62 + UP * 0.25),
        )
        self.add(triangle, altitude, right_angle, angle, points, title(r"\triangle ABC"), labels)


class ProbabilityScene(FigurizeBaseScene):
    def construct(self):
        axes = axes_2d((-4, 4, 1), (0, 0.5, 0.1))
        density = lambda x: math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
        curve = axes.plot(density, x_range=[-4, 4], color=BLUE, stroke_width=4.0)
        area = axes.get_area(curve, x_range=[-1, 1], color=GREEN, opacity=0.36)
        bounds = VGroup(
            DashedLine(axes.c2p(-1, 0), axes.c2p(-1, density(-1)), color=GREEN, stroke_width=1.3),
            DashedLine(axes.c2p(1, 0), axes.c2p(1, density(1)), color=GREEN, stroke_width=1.3),
        )
        label = math_label(r"P(-1\leq X\leq 1)", GREEN, 30).move_to(axes.c2p(0, 0.21))
        self.add(area, axes, curve, bounds, title(r"X\sim\mathcal N(0,1)"), label)


class ScatterScene(FigurizeBaseScene):
    def construct(self):
        axes = axes_2d((0, 9, 1), (0, 9, 1))
        samples = [(1, 2), (2, 2.7), (3, 3.8), (4, 4.4), (5, 5.6), (6, 6.1), (7, 7.2), (8, 7.7)]
        dots = VGroup(*[filled_point(axes.c2p(x, y), BLUE, 0.055) for x, y in samples])
        trend = axes.plot(lambda x: 0.83 * x + 1.15, x_range=[0.7, 8.3], color=PURPLE, stroke_width=2.8)
        labels = VGroup(
            math_label("d", PURPLE, 28).move_to(axes.c2p(7.8, 7.85)),
            text_label("observations", BLUE, 24).move_to(axes.c2p(2.0, 7.7)),
        )
        self.add(axes, dots, trend, title(r"\text{Scatter and trend}"), labels)


class HistogramScene(FigurizeBaseScene):
    def construct(self):
        axes = axes_2d((-1, 5, 1), (-3, 4, 1))
        values = [2.0, -1.5, 3.0, -2.2, 1.4]
        bars = VGroup()
        for index, value in enumerate(values):
            color = GREEN if value >= 0 else WARM_RED
            bar = Rectangle(
                width=axes.x_axis.get_unit_size() * 0.7,
                height=abs(value) * axes.y_axis.get_unit_size(),
                stroke_color=color,
                stroke_width=1.3,
                fill_color=color,
                fill_opacity=0.42,
            )
            bar.move_to(axes.c2p(index, value / 2))
            bars.add(bar)
        self.add(axes, bars, title(r"\text{Signed quantities}"))


class UnitCircleScene(FigurizeBaseScene):
    def construct(self):
        center = LEFT * 3.5
        radius = 1.55
        circle = Circle(radius=radius, color=BLUE, stroke_width=3.0).move_to(center)
        circle_axes = VGroup(
            Line(center + LEFT * 1.9, center + RIGHT * 1.9, color=GRAPHITE, stroke_width=1.4),
            Line(center + DOWN * 1.9, center + UP * 1.9, color=GRAPHITE, stroke_width=1.4),
        )
        angles = [math.pi / 3, 5 * math.pi / 3]
        points = VGroup()
        radii = VGroup()
        for angle_value in angles:
            endpoint = center + radius * np.array([math.cos(angle_value), math.sin(angle_value), 0])
            radii.add(Line(center, endpoint, color=GREEN, stroke_width=1.5))
            points.add(filled_point(endpoint, PURPLE))
        graph_axes = Axes(
            x_range=[0, TAU, math.pi / 2],
            y_range=[-1.2, 1.2, 0.5],
            x_length=5.7,
            y_length=3.4,
            tips=False,
            axis_config={"color": GRAPHITE, "stroke_width": 1.4},
        ).shift(RIGHT * 3.0)
        graph = graph_axes.plot(math.cos, x_range=[0, TAU], color=BLUE, stroke_width=3.3)
        target_line = Line(graph_axes.c2p(0, 0.5), graph_axes.c2p(TAU, 0.5), color=GREEN, stroke_width=1.8)
        graph_points = VGroup(*[filled_point(graph_axes.c2p(value, 0.5), PURPLE) for value in angles])
        labels = VGroup(
            math_label(r"\pi/3", PURPLE, 25).next_to(graph_points[0], DOWN, buff=0.12),
            math_label(r"5\pi/3", PURPLE, 25).next_to(graph_points[1], DOWN, buff=0.12),
        )
        self.add(circle_axes, circle, radii, points, graph_axes, graph, target_line, graph_points, title(r"\cos x=\frac12"), labels)


class SurfaceTangentPlaneScene(FigurizeBaseScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 4, 1],
            x_length=5.8,
            y_length=5.8,
            z_length=4.1,
            axis_config={"color": GRAPHITE, "stroke_width": 1.5, "tip_shape": StealthTip},
        )
        small_axis_tips_3d(axes)
        self.set_camera_orientation(phi=67 * DEGREES, theta=-52 * DEGREES, zoom=0.82)
        f = lambda x, y: 0.45 * x * x + 0.3 * y * y
        surface = Surface(
            lambda u, v: axes.c2p(u, v, f(u, v)),
            u_range=[-2, 2],
            v_range=[-2, 2],
            resolution=(26, 26),
            checkerboard_colors=[BLUE, BLUE_LIGHT],
            fill_opacity=0.72,
            stroke_width=0.3,
        )
        x0, y0 = 0.85, 0.65
        z0 = f(x0, y0)
        fx, fy = 0.9 * x0, 0.6 * y0
        plane = Surface(
            lambda u, v: axes.c2p(u, v, z0 + fx * (u - x0) + fy * (v - y0)),
            u_range=[x0 - 0.85, x0 + 0.85],
            v_range=[y0 - 0.85, y0 + 0.85],
            resolution=(6, 6),
            checkerboard_colors=[PURPLE, PURPLE_LIGHT],
            fill_opacity=0.58,
            stroke_width=0.5,
        )
        point = Dot3D(axes.c2p(x0, y0, z0), radius=0.075, color=PURPLE)
        normal = Arrow3D(
            start=axes.c2p(x0, y0, z0),
            end=axes.c2p(x0 - 0.72 * fx, y0 - 0.72 * fy, z0 + 0.72),
            color=GREEN,
            thickness=0.022,
            height=0.16,
            base_radius=0.06,
        )
        fixed = VGroup(
            title(r"f(x,y)=0.45x^2+0.30y^2"),
            math_label(r"T_A", PURPLE, 28).to_corner(UP + RIGHT, buff=0.35),
            math_label(r"\vec n", GREEN, 28).to_corner(DOWN + RIGHT, buff=0.35),
        )
        self.add_fixed_in_frame_mobjects(*fixed)
        self.add(axes, surface, plane, point, normal)


class HelixScene(FigurizeBaseScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 3, 1],
            x_length=5.5,
            y_length=5.5,
            z_length=4.2,
            axis_config={"color": GRAPHITE, "stroke_width": 1.5, "tip_shape": StealthTip},
        )
        small_axis_tips_3d(axes)
        self.set_camera_orientation(phi=66 * DEGREES, theta=-48 * DEGREES, zoom=0.85)
        curve = ParametricFunction(
            lambda t: axes.c2p(math.cos(t), math.sin(t), 0.18 * t),
            t_range=[0, 4 * math.pi],
            color=BLUE,
            stroke_width=3.5,
        )
        fixed = VGroup(title(r"\gamma(t)=(\cos t,\sin t,0.18t)"), math_label(r"\gamma", BLUE, 29).to_corner(UP + RIGHT, buff=0.35))
        self.add_fixed_in_frame_mobjects(*fixed)
        self.add(axes, curve)


class LinearTransformAnimationScene(FigurizeBaseScene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            x_length=9.4,
            y_length=5.3,
            axis_config={"color": GRAPHITE, "stroke_width": 1.7, "tip_shape": StealthTip},
            background_line_style={"stroke_color": GRID, "stroke_width": 0.8, "stroke_opacity": 0.4},
        )
        small_axis_tips(plane)
        origin = plane.c2p(0, 0)
        e1 = Arrow(origin, plane.c2p(1, 0), buff=0, color=BLUE, stroke_width=3.0)
        e2 = Arrow(origin, plane.c2p(0, 1), buff=0, color=GREEN, stroke_width=3.0)
        heading = title(r"A=\begin{pmatrix}1&0.85\\0.25&1\end{pmatrix}")
        self.play(FadeIn(heading), Create(plane), FadeIn(e1), FadeIn(e2), run_time=1.0)
        self.play(
            ApplyMatrix([[1, 0.85], [0.25, 1]], plane),
            ApplyMatrix([[1, 0.85], [0.25, 1]], e1),
            ApplyMatrix([[1, 0.85], [0.25, 1]], e2),
            run_time=2.2,
        )
        self.wait(0.6)


class SignedAreaAnimationScene(FigurizeBaseScene):
    def construct(self):
        axes = axes_2d((-2.5, 2.5, 1), (-3.4, 3.4, 1))
        f = lambda x: x**3 - 2 * x
        curve = axes.plot(f, x_range=[-2.05, 2.05], color=BLUE, stroke_width=4.0)
        root = math.sqrt(2)
        intervals = [
            (-2.0, -root, WARM_RED),
            (-root, 0.0, GREEN),
            (0.0, root, WARM_RED),
            (root, 2.0, GREEN),
        ]
        areas = [axes.get_area(curve, x_range=[left, right], color=color, opacity=0.34) for left, right, color in intervals]
        self.play(FadeIn(title(r"f(x)=x^3-2x")), FadeIn(axes), Create(curve), run_time=1.2)
        for area in areas:
            self.play(FadeIn(area), run_time=0.55)
        self.wait(0.5)
