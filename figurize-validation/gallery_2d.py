from __future__ import annotations

import numpy as np
from manim import (
    Angle,
    Arc,
    Arrow,
    ArrowVectorField,
    Axes,
    BraceBetweenPoints,
    Circle,
    DashedLine,
    Dot,
    DOWN,
    LEFT,
    Line,
    MathTex,
    NumberPlane,
    ORIGIN,
    Polygon,
    Rectangle,
    RIGHT,
    Square,
    Text,
    UP,
    VGroup,
)

from components import (
    FigurizeScene,
    angle_code,
    caption,
    component_card,
    dimension_marker,
    distance_marker,
    labeled_point,
    legend,
    make_axes_2d,
    make_number_line,
    make_number_plane,
    math_title,
    open_point_marker,
    point_marker,
    projection_guides,
    semantic_tick,
    title_group,
    vector_arrow,
)
from theme import (
    ATTENTION_PRIMARY,
    AXIS_PRIMARY,
    BACKGROUND_DARK,
    BACKGROUND_LIGHT,
    CONSTRUCTION_AUXILIARY,
    DATA_POINT,
    DATA_TREND,
    DERIVATIVE_PRIMARY,
    FUNCTION_PRIMARY,
    FUNCTION_SECONDARY,
    GRID_MAJOR,
    GRID_MINOR,
    LEVEL_CURVE_PRIMARY,
    POINT_ARBITRARY,
    POINT_CRITICAL,
    POINT_DEFAULT,
    POINT_HIGHLIGHT,
    PROBABILITY_EVENT,
    PROJECTION_GUIDE,
    REGION_PRIMARY,
    REGION_SECONDARY,
    STROKE_EMPHASIZED,
    STROKE_NORMAL,
    STROKE_STRONG,
    STROKE_THIN,
    TANGENT_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    VECTOR_DEFAULT,
    VECTOR_HIGHLIGHT,
)


class PrimitiveComponents(FigurizeScene):
    """Visual inventory of the first reusable primitives."""

    def construct(self):
        heading = title_group(
            "Figurize primitive components",
            "Each component keeps a semantic role independent from its concrete color.",
        ).to_edge(UP, buff=0.3)

        point_body = VGroup(
            point_marker(LEFT * 0.72, "default"),
            point_marker(LEFT * 0.24, "highlight"),
            point_marker(RIGHT * 0.24, "arbitrary"),
            open_point_marker(RIGHT * 0.72, color=POINT_DEFAULT),
        )
        point_labels = VGroup(
            Text("ordinary", font_size=14, color=TEXT_MUTED).next_to(point_body[0], DOWN, buff=0.11),
            Text("highlight", font_size=14, color=TEXT_MUTED).next_to(point_body[1], DOWN, buff=0.11),
            Text("arbitrary", font_size=14, color=TEXT_MUTED).next_to(point_body[2], DOWN, buff=0.11),
            Text("excluded", font_size=14, color=TEXT_MUTED).next_to(point_body[3], DOWN, buff=0.11),
        )
        points_card = component_card("Point markers", VGroup(point_body, point_labels))

        line_1 = Line(LEFT * 1.0, RIGHT * 1.0, color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED)
        line_2 = DashedLine(LEFT * 1.0, RIGHT * 1.0, color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_THIN)
        line_2.shift(DOWN * 0.42)
        arrow = Arrow(LEFT * 1.0, RIGHT * 1.0, buff=0, color=VECTOR_DEFAULT, stroke_width=STROKE_EMPHASIZED)
        arrow.shift(UP * 0.42)
        lines_card = component_card("Lines and arrows", VGroup(arrow, line_1, line_2))

        triangle = Polygon(
            LEFT * 0.9 + DOWN * 0.55,
            RIGHT * 0.85 + DOWN * 0.55,
            LEFT * 0.25 + UP * 0.75,
            color=FUNCTION_PRIMARY,
            stroke_width=STROKE_NORMAL,
        )
        circle = Circle(radius=0.46, color=FUNCTION_SECONDARY, stroke_width=STROKE_NORMAL).shift(RIGHT * 0.73)
        arc = Arc(radius=0.55, start_angle=0.2, angle=1.7, color=ATTENTION_PRIMARY, stroke_width=STROKE_NORMAL).shift(LEFT * 0.65)
        shapes_card = component_card("Planar shapes", VGroup(triangle, circle, arc).scale(0.78))

        A = LEFT * 0.9 + DOWN * 0.35
        B = RIGHT * 0.95 + DOWN * 0.35
        C = LEFT * 0.35 + UP * 0.65
        l1 = Line(A, B, color=AXIS_PRIMARY)
        l2 = Line(A, C, color=AXIS_PRIMARY)
        ang = Angle(l1, l2, radius=0.36, color=POINT_HIGHLIGHT, stroke_width=STROKE_NORMAL)
        measure = MathTex(r"42^\circ", font_size=22, color=TEXT_PRIMARY).move_to(A + RIGHT * 0.58 + UP * 0.25)
        dim = dimension_marker(A, B, "d", offset=DOWN * 0.3).scale(0.82)
        annotations_card = component_card("Annotations", VGroup(l1, l2, ang, measure, dim).scale(0.9))

        cards = VGroup(points_card, lines_card, shapes_card, annotations_card)
        cards.arrange_in_grid(rows=2, cols=2, buff=(0.45, 0.42))
        cards.next_to(heading, DOWN, buff=0.38)
        self.add(heading, cards)


class AxisTicksGrid(FigurizeScene):
    def construct(self):
        heading = title_group(
            "Axes, ticks and grids",
            "Sparse major ticks, semantic ticks and a low-priority grid.",
        ).to_edge(UP, buff=0.3)
        plane = make_number_plane(x_range=(-4, 4, 1), y_range=(-3, 3, 1), x_length=10.2, y_length=5.3)
        plane.next_to(heading, DOWN, buff=0.35)
        curve = plane.plot(lambda x: 0.45 * x + 0.8, x_range=[-3.5, 3.5], color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED)
        ticks = VGroup(
            semantic_tick(plane, axis="x", value=2, label="a"),
            semantic_tick(plane, axis="y", value=1.7, label="f(a)"),
        )
        point = point_marker(plane.c2p(2, 1.7), "highlight")
        guides = projection_guides(plane, 2, 1.7)
        self.add(heading, plane, curve, guides, ticks, point)


class IntervalComponents(FigurizeScene):
    def construct(self):
        heading = title_group(
            "Intervals as reusable components",
            "The same grammar supports domains, inequalities, probability and timelines.",
        ).to_edge(UP, buff=0.28)
        rows = VGroup()
        specs = [
            (r"[-2,3]", -2, 3, True, True, FUNCTION_PRIMARY),
            (r"(-2,3)", -2, 3, False, False, FUNCTION_SECONDARY),
            (r"[-2,3)", -2, 3, True, False, POINT_HIGHLIGHT),
            (r"(-\infty,1]\cup(3,+\infty)", -4, 1, False, True, TANGENT_PRIMARY),
        ]
        for index, (label, start, end, closed_left, closed_right, color) in enumerate(specs):
            line = make_number_line((-4, 5, 1), length=9.2, include_numbers=False)
            if index < 3:
                segment = Line(line.n2p(start), line.n2p(end), color=color, stroke_width=7)
                left_marker = point_marker(line.n2p(start), "default") if closed_left else open_point_marker(line.n2p(start), color=color)
                right_marker = point_marker(line.n2p(end), "default") if closed_right else open_point_marker(line.n2p(end), color=color)
                body = VGroup(line, segment, left_marker, right_marker)
            else:
                left_ray = Line(line.n2p(-4), line.n2p(1), color=color, stroke_width=7)
                right_ray = Line(line.n2p(3), line.n2p(5), color=color, stroke_width=7)
                body = VGroup(
                    line,
                    left_ray,
                    right_ray,
                    point_marker(line.n2p(1), "default"),
                    open_point_marker(line.n2p(3), color=color),
                )
            formula = MathTex(label, font_size=28, color=TEXT_PRIMARY)
            formula.next_to(body, LEFT, buff=0.45)
            rows.add(VGroup(formula, body))
        rows.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        rows.scale(0.75)
        rows.next_to(heading, DOWN, buff=0.35)
        self.add(heading, rows)


class CartesianComponents(FigurizeScene):
    def construct(self):
        heading = title_group(
            "Points, vectors and projections",
            "A single coordinate frame composes symbolic and numeric objects.",
        ).to_edge(UP, buff=0.28)
        axes = make_axes_2d((-4, 4, 1), (-3, 3, 1), x_length=9.8, y_length=5.2)
        axes.next_to(heading, DOWN, buff=0.32)
        A = axes.c2p(2, 1.25)
        B = axes.c2p(-1.4, 2.05)
        a = labeled_point(A, r"A(2,1.25)", role="highlight", direction=UP + RIGHT)
        b = labeled_point(B, r"B(-1.4,2.05)", role="arbitrary", direction=UP + LEFT)
        guides = projection_guides(axes, 2, 1.25, x_label="2", y_label="1.25")
        vector = vector_arrow(axes.c2p(0, 0), axes.c2p(2.8, 2.0), r"\vec v")
        dist = distance_marker(B, A, r"d(A,B)", label_direction=UP)
        self.add(heading, axes, guides, dist, vector, a, b)


class GeometryComponents(FigurizeScene):
    def construct(self):
        heading = title_group(
            "Geometry with semantic codes",
            "Angles, perpendicularity, distances, labels and area remain separate components.",
        ).to_edge(UP, buff=0.28)
        A = LEFT * 4.2 + DOWN * 2.0
        B = RIGHT * 3.8 + DOWN * 2.0
        C = LEFT * 1.7 + UP * 2.1
        triangle = Polygon(A, B, C, color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED)
        triangle.set_fill(REGION_PRIMARY, opacity=0.13)
        H = np.array([C[0], A[1], 0])
        altitude = DashedLine(C, H, color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_THIN)
        right_square = Square(side_length=0.28, color=POINT_HIGHLIGHT, stroke_width=STROKE_NORMAL)
        right_square.move_to(H + RIGHT * 0.14 + UP * 0.14)
        line_ab = Line(A, B)
        line_ac = Line(A, C)
        angle = angle_code(line_ab, line_ac, r"42^\circ", radius=0.55)
        labels = VGroup(
            MathTex("A", font_size=28, color=TEXT_PRIMARY).next_to(A, DOWN + LEFT, buff=0.12),
            MathTex("B", font_size=28, color=TEXT_PRIMARY).next_to(B, DOWN + RIGHT, buff=0.12),
            MathTex("C", font_size=28, color=TEXT_PRIMARY).next_to(C, UP, buff=0.12),
            MathTex("H", font_size=24, color=TEXT_SECONDARY).next_to(H, DOWN, buff=0.12),
            MathTex("h", font_size=26, color=TEXT_SECONDARY).next_to(altitude, RIGHT, buff=0.12),
        )
        base_dimension = dimension_marker(A, B, "b", offset=DOWN * 0.5)
        area = MathTex(r"\mathcal A=\frac{bh}{2}", font_size=32, color=TEXT_PRIMARY)
        area.move_to((A + B + C) / 3 + RIGHT * 0.45)
        heading.move_to(UP * 3.35)
        self.add(heading, triangle, altitude, right_square, angle, labels, base_dimension, area)


class FunctionBasic(FigurizeScene):
    def construct(self):
        heading = math_title(r"f(x)=x^3-2x+1", "Canonical one-variable function plot").to_edge(UP, buff=0.28)
        axes = make_axes_2d((-3, 3, 1), (-5, 7, 1), x_length=8.8, y_length=5.4)
        axes.next_to(heading, DOWN, buff=0.3)
        curve = axes.plot(lambda x: x**3 - 2 * x + 1, x_range=[-2.25, 2.25], color=FUNCTION_PRIMARY, stroke_width=STROKE_STRONG)
        label = MathTex("f", font_size=28, color=FUNCTION_PRIMARY).next_to(curve.get_end(), UP + LEFT, buff=0.12)
        self.add(heading, axes, curve, label)


class FunctionEvaluation(FigurizeScene):
    def construct(self):
        heading = math_title(r"f(x)=x^3-2x+1,\qquad f(2)=5", "Evaluation point and semantic projections").to_edge(UP, buff=0.28)
        axes = make_axes_2d((-2.5, 3, 1), (-4, 7, 1), x_length=8.6, y_length=5.4)
        axes.next_to(heading, DOWN, buff=0.3)
        curve = axes.plot(lambda x: x**3 - 2 * x + 1, x_range=[-2.0, 2.35], color=FUNCTION_PRIMARY, stroke_width=STROKE_STRONG)
        P = axes.c2p(2, 5)
        guides = projection_guides(axes, 2, 5, x_label="2", y_label="5")
        point = labeled_point(P, r"(2,5)", role="highlight", direction=UP + RIGHT)
        self.add(heading, axes, curve, guides, point)


class FunctionRootsTangents(FigurizeScene):
    def construct(self):
        heading = math_title(
            r"f(x)=x^3-2x+1",
            "Roots, critical points and horizontal tangents composed on one canonical plot",
        ).to_edge(UP, buff=0.25)
        axes = make_axes_2d((-3, 3, 1), (-5, 7, 1), x_length=8.8, y_length=5.25)
        axes.next_to(heading, DOWN, buff=0.28)
        curve = axes.plot(lambda x: x**3 - 2 * x + 1, x_range=[-2.25, 2.25], color=FUNCTION_PRIMARY, stroke_width=STROKE_STRONG)
        roots = [(-1 - np.sqrt(5)) / 2, (-1 + np.sqrt(5)) / 2, 1.0]
        root_markers = VGroup(*[point_marker(axes.c2p(root, 0), "highlight") for root in roots])
        root_labels = VGroup(*[
            MathTex(label, font_size=20, color=TEXT_SECONDARY).next_to(axes.c2p(root, 0), DOWN, buff=0.14)
            for root, label in zip(roots, [r"\frac{-1-\sqrt5}{2}", r"\frac{-1+\sqrt5}{2}", "1"])
        ])
        critical_x = [-np.sqrt(2 / 3), np.sqrt(2 / 3)]
        tangent_group = VGroup()
        critical_group = VGroup()
        for x_value in critical_x:
            y_value = x_value**3 - 2 * x_value + 1
            critical_group.add(point_marker(axes.c2p(x_value, y_value), "critical"))
            tangent_group.add(
                Line(
                    axes.c2p(x_value - 0.75, y_value),
                    axes.c2p(x_value + 0.75, y_value),
                    color=TANGENT_PRIMARY,
                    stroke_width=STROKE_EMPHASIZED,
                )
            )
        key = legend([
            ("function", FUNCTION_PRIMARY),
            ("roots", POINT_HIGHLIGHT),
            ("horizontal tangents", TANGENT_PRIMARY),
        ]).scale(0.85).to_corner(RIGHT + UP, buff=0.35).shift(DOWN * 0.8)
        self.add(heading, axes, curve, tangent_group, root_markers, root_labels, critical_group, key)


class ArbitraryPointOnCurve(FigurizeScene):
    def construct(self):
        heading = math_title(r"A=(x,f(x))", "A deterministic representative position without inventing numeric coordinates").to_edge(UP, buff=0.28)
        axes = make_axes_2d((-4, 4, 1), (-2.5, 4, 1), x_length=9.3, y_length=5.2)
        axes.next_to(heading, DOWN, buff=0.3)
        fn = lambda t: 0.22 * (t + 1.0) ** 2 - 0.35
        curve = axes.plot(fn, x_range=[-3.5, 3.4], color=FUNCTION_PRIMARY, stroke_width=STROKE_STRONG)
        representative_x = 1.35
        representative_y = fn(representative_x)
        point = labeled_point(
            axes.c2p(representative_x, representative_y),
            r"A(x,f(x))",
            role="arbitrary",
            direction=UP + RIGHT,
        )
        guides = projection_guides(
            axes,
            representative_x,
            representative_y,
            x_label="x",
            y_label="f(x)",
        )
        note = caption("The location is representative; the coordinates remain symbolic.")
        note.to_edge(DOWN, buff=0.25)
        self.add(heading, axes, curve, guides, point, note)


class AreaUnderCurve(FigurizeScene):
    def construct(self):
        heading = math_title(r"\int_a^b f(x)\,dx", "Function, bounds and highlighted area").to_edge(UP, buff=0.28)
        axes = make_axes_2d((-1, 6, 1), (-1, 5, 1), x_length=9.4, y_length=5.2)
        axes.next_to(heading, DOWN, buff=0.3)
        fn = lambda x: 0.22 * (x - 2.6) ** 2 + 1.0
        curve = axes.plot(fn, x_range=[0, 5.3], color=FUNCTION_PRIMARY, stroke_width=STROKE_STRONG)
        a, b = 1.0, 4.5
        area = axes.get_area(curve, x_range=[a, b], color=REGION_PRIMARY, opacity=0.38)
        guides = VGroup(
            DashedLine(axes.c2p(a, 0), axes.c2p(a, fn(a)), color=PROJECTION_GUIDE, stroke_width=STROKE_THIN),
            DashedLine(axes.c2p(b, 0), axes.c2p(b, fn(b)), color=PROJECTION_GUIDE, stroke_width=STROKE_THIN),
            semantic_tick(axes, axis="x", value=a, label="a"),
            semantic_tick(axes, axis="x", value=b, label="b"),
        )
        self.add(heading, axes, area, curve, guides)


class AlgebraAreaIdentity(FigurizeScene):
    def construct(self):
        heading = math_title(r"x^2+2x+1=(x+1)^2", "An algebraic identity formalized as a decomposition of area").to_edge(UP, buff=0.28)
        x_side = 2.35
        one_side = 0.82
        total = x_side + one_side
        origin = LEFT * 1.6 + DOWN * 1.9
        square_x = Rectangle(width=x_side, height=x_side, color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED, fill_color=REGION_PRIMARY, fill_opacity=0.24)
        square_x.move_to(origin + RIGHT * x_side / 2 + UP * x_side / 2)
        rect_top = Rectangle(width=x_side, height=one_side, color=FUNCTION_SECONDARY, stroke_width=STROKE_NORMAL, fill_color=REGION_SECONDARY, fill_opacity=0.24)
        rect_top.move_to(origin + RIGHT * x_side / 2 + UP * (x_side + one_side / 2))
        rect_right = Rectangle(width=one_side, height=x_side, color=FUNCTION_SECONDARY, stroke_width=STROKE_NORMAL, fill_color=REGION_SECONDARY, fill_opacity=0.24)
        rect_right.move_to(origin + RIGHT * (x_side + one_side / 2) + UP * x_side / 2)
        square_one = Square(side_length=one_side, color=POINT_HIGHLIGHT, stroke_width=STROKE_NORMAL, fill_color=POINT_HIGHLIGHT, fill_opacity=0.18)
        square_one.move_to(origin + RIGHT * (x_side + one_side / 2) + UP * (x_side + one_side / 2))
        outer = Square(side_length=total, color=AXIS_PRIMARY, stroke_width=STROKE_EMPHASIZED)
        outer.move_to(origin + RIGHT * total / 2 + UP * total / 2)
        labels = VGroup(
            MathTex("x^2", font_size=34, color=TEXT_PRIMARY).move_to(square_x),
            MathTex("x", font_size=30, color=TEXT_PRIMARY).move_to(rect_top),
            MathTex("x", font_size=30, color=TEXT_PRIMARY).move_to(rect_right),
            MathTex("1", font_size=28, color=TEXT_PRIMARY).move_to(square_one),
            MathTex("x", font_size=26, color=TEXT_SECONDARY).next_to(square_x, LEFT, buff=0.16),
            MathTex("1", font_size=26, color=TEXT_SECONDARY).next_to(rect_top, LEFT, buff=0.16),
            MathTex("x", font_size=26, color=TEXT_SECONDARY).next_to(square_x, DOWN, buff=0.16),
            MathTex("1", font_size=26, color=TEXT_SECONDARY).next_to(rect_right, DOWN, buff=0.16),
        )
        explanation = VGroup(
            MathTex(r"x^2", font_size=32, color=FUNCTION_PRIMARY),
            MathTex(r"+\,x+x", font_size=32, color=FUNCTION_SECONDARY),
            MathTex(r"+\,1", font_size=32, color=POINT_HIGHLIGHT),
            MathTex(r"=\,(x+1)^2", font_size=32, color=TEXT_PRIMARY),
        ).arrange(RIGHT, buff=0.13)
        explanation.next_to(outer, RIGHT, buff=0.8)
        self.add(heading, outer, square_x, rect_top, rect_right, square_one, labels, explanation)


class UnitCircleCosEquation(FigurizeScene):
    def construct(self):
        heading = math_title(r"\cos(x)=\frac12,\qquad x\in[0,2\pi]", "Unit circle and function graph share the same solutions").to_edge(UP, buff=0.25)
        center = LEFT * 3.7 + DOWN * 0.35
        radius = 1.65
        circle = Circle(radius=radius, color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED).move_to(center)
        circle_axes = VGroup(
            Line(center + LEFT * 2.0, center + RIGHT * 2.0, color=AXIS_PRIMARY, stroke_width=STROKE_THIN),
            Line(center + DOWN * 2.0, center + UP * 2.0, color=AXIS_PRIMARY, stroke_width=STROKE_THIN),
        )
        angles = [np.pi / 3, 5 * np.pi / 3]
        circle_points = VGroup()
        radii = VGroup()
        for angle_value in angles:
            endpoint = center + radius * np.array([np.cos(angle_value), np.sin(angle_value), 0.0])
            radii.add(Line(center, endpoint, color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_THIN))
            circle_points.add(point_marker(endpoint, "highlight"))
        x_projection = DashedLine(
            center + np.array([radius / 2, -radius, 0]),
            center + np.array([radius / 2, radius, 0]),
            color=PROJECTION_GUIDE,
            stroke_width=STROKE_THIN,
        )
        half_label = MathTex(r"\frac12", font_size=24, color=TEXT_SECONDARY).next_to(center + RIGHT * radius / 2, DOWN, buff=0.12)

        axes = make_axes_2d((0, 2 * np.pi, np.pi / 2), (-1.3, 1.3, 0.5), x_length=6.0, y_length=3.7, tips=False)
        axes.shift(RIGHT * 2.75 + DOWN * 0.35)
        graph = axes.plot(np.cos, x_range=[0, 2 * np.pi], color=FUNCTION_SECONDARY, stroke_width=STROKE_STRONG)
        half_line = Line(axes.c2p(0, 0.5), axes.c2p(2 * np.pi, 0.5), color=PROBABILITY_EVENT, stroke_width=STROKE_NORMAL)
        graph_points = VGroup(*[point_marker(axes.c2p(value, 0.5), "highlight") for value in angles])
        graph_labels = VGroup(
            MathTex(r"\frac{\pi}{3}", font_size=22, color=TEXT_PRIMARY).next_to(axes.c2p(np.pi / 3, 0), DOWN, buff=0.12),
            MathTex(r"\frac{5\pi}{3}", font_size=22, color=TEXT_PRIMARY).next_to(axes.c2p(5 * np.pi / 3, 0), DOWN, buff=0.12),
        )
        self.add(heading, circle_axes, circle, radii, x_projection, circle_points, half_label, axes, graph, half_line, graph_points, graph_labels)


class ProbabilityNormalRegion(FigurizeScene):
    def construct(self):
        heading = math_title(r"X\sim\mathcal N(0,1),\qquad P(-1\leq X\leq1)", "An event represented as a region under a density curve").to_edge(UP, buff=0.27)
        axes = make_axes_2d((-4, 4, 1), (0, 0.5, 0.1), x_length=9.4, y_length=4.8, tips=False)
        axes.next_to(heading, DOWN, buff=0.35)
        density = lambda x: np.exp(-(x**2) / 2) / np.sqrt(2 * np.pi)
        curve = axes.plot(density, x_range=[-4, 4], color=FUNCTION_PRIMARY, stroke_width=STROKE_STRONG)
        area = axes.get_area(curve, x_range=[-1, 1], color=PROBABILITY_EVENT, opacity=0.4)
        bounds = VGroup(
            DashedLine(axes.c2p(-1, 0), axes.c2p(-1, density(-1)), color=PROJECTION_GUIDE, stroke_width=STROKE_THIN),
            DashedLine(axes.c2p(1, 0), axes.c2p(1, density(1)), color=PROJECTION_GUIDE, stroke_width=STROKE_THIN),
            semantic_tick(axes, axis="x", value=-1, label="-1"),
            semantic_tick(axes, axis="x", value=1, label="1"),
        )
        self.add(heading, axes, area, curve, bounds)


class ScatterRegression(FigurizeScene):
    def construct(self):
        heading = title_group(
            "Scatter plot and trend",
            "Data points and the fitted trend use distinct semantic roles.",
        ).to_edge(UP, buff=0.28)
        axes = make_axes_2d((0, 10, 1), (0, 10, 1), x_length=8.5, y_length=5.2, tips=False)
        axes.next_to(heading, DOWN, buff=0.32)
        points = [(1.0, 2.0), (1.8, 2.6), (2.5, 3.4), (3.2, 3.7), (4.1, 4.9), (5.1, 5.2), (5.8, 6.4), (6.7, 6.6), (7.5, 7.8), (8.6, 8.2)]
        dots = VGroup(*[Dot(axes.c2p(x, y), radius=0.065, color=DATA_POINT) for x, y in points])
        trend = axes.plot(lambda x: 0.82 * x + 1.15, x_range=[0.6, 9.1], color=DATA_TREND, stroke_width=STROKE_EMPHASIZED)
        upper = [axes.c2p(x, 0.82 * x + 1.75) for x in np.linspace(0.6, 9.1, 18)]
        lower = [axes.c2p(x, 0.82 * x + 0.55) for x in np.linspace(9.1, 0.6, 18)]
        band = Polygon(*(upper + lower), color=DATA_TREND, stroke_opacity=0, fill_color=DATA_TREND, fill_opacity=0.1)
        key = legend([("observations", DATA_POINT), ("trend", DATA_TREND)]).scale(0.85).to_corner(RIGHT + UP, buff=0.4).shift(DOWN * 0.8)
        self.add(heading, axes, band, dots, trend, key)


class VectorFieldComposition(FigurizeScene):
    def construct(self):
        heading = math_title(r"F(x,y)=(-y,x)", "Vector field, trajectories and a highlighted vector").to_edge(UP, buff=0.27)
        plane = make_number_plane((-3, 3, 1), (-3, 3, 1), x_length=8.0, y_length=5.3)
        plane.next_to(heading, DOWN, buff=0.32)
        field = ArrowVectorField(
            lambda p: np.array([-p[1], p[0], 0.0]),
            x_range=[-3, 3, 0.65],
            y_range=[-3, 3, 0.65],
            colors=[FUNCTION_PRIMARY, FUNCTION_SECONDARY],
            length_func=lambda norm: 0.42,
        )
        field.move_to(plane)
        trajectories = VGroup(*[
            Circle(radius=plane.x_axis.get_unit_size() * r, color=LEVEL_CURVE_PRIMARY, stroke_width=STROKE_THIN, stroke_opacity=0.7).move_to(plane.c2p(0, 0))
            for r in (0.8, 1.55, 2.25)
        ])
        p = plane.c2p(1.45, 0.85)
        highlighted = vector_arrow(p, p + np.array([-0.85, 1.45, 0]) * 0.48, r"F(A)", color=VECTOR_HIGHLIGHT)
        A = labeled_point(p, "A", role="highlight", direction=DOWN + RIGHT)
        self.add(heading, plane, trajectories, field, A, highlighted)


class LinearTransformationStatic(FigurizeScene):
    def construct(self):
        heading = math_title(r"A=\begin{pmatrix}1&0.85\\0.25&1\end{pmatrix}", "Before and after applying a linear transformation").to_edge(UP, buff=0.25)
        base = NumberPlane(
            x_range=[-2.4, 2.4, 0.5],
            y_range=[-2.0, 2.0, 0.5],
            x_length=5.0,
            y_length=4.1,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.6},
            background_line_style={"stroke_color": GRID_MAJOR, "stroke_width": 1.0, "stroke_opacity": 0.42},
        )
        left_plane = base.copy().shift(LEFT * 3.4 + DOWN * 0.45)
        right_plane = base.copy()
        matrix = np.array([[1.0, 0.85], [0.25, 1.0]])
        right_plane.apply_matrix(matrix)
        right_plane.shift(RIGHT * 3.4 + DOWN * 0.45)
        left_vectors = VGroup(
            Arrow(left_plane.c2p(0, 0), left_plane.c2p(1, 0), buff=0, color=VECTOR_HIGHLIGHT),
            Arrow(left_plane.c2p(0, 0), left_plane.c2p(0, 1), buff=0, color=TANGENT_PRIMARY),
        )
        origin_right = right_plane.c2p(0, 0)
        right_vectors = VGroup(
            Arrow(origin_right, right_plane.c2p(1, 0), buff=0, color=VECTOR_HIGHLIGHT),
            Arrow(origin_right, right_plane.c2p(0, 1), buff=0, color=TANGENT_PRIMARY),
        )
        labels = VGroup(
            Text("input space", font_size=22, color=TEXT_SECONDARY).next_to(left_plane, DOWN, buff=0.18),
            Text("transformed space", font_size=22, color=TEXT_SECONDARY).next_to(right_plane, DOWN, buff=0.18),
            Arrow(LEFT * 0.65 + DOWN * 0.35, RIGHT * 0.65 + DOWN * 0.35, color=ATTENTION_PRIMARY, stroke_width=STROKE_EMPHASIZED),
        )
        self.add(heading, left_plane, right_plane, left_vectors, right_vectors, labels)


class DarkBackgroundPreview(FigurizeScene):
    def setup(self):
        super().setup()
        self.camera.background_color = BACKGROUND_DARK

    def construct(self):
        heading = MathTex(r"f(x)=\sin x", font_size=34, color="#F8FAFC").to_edge(UP, buff=0.3)
        axes = Axes(
            x_range=[-2 * np.pi, 2 * np.pi, np.pi],
            y_range=[-1.5, 1.5, 0.5],
            x_length=10.0,
            y_length=4.8,
            tips=True,
            axis_config={"color": "#E2E8F0", "stroke_width": 2.0},
        )
        curve = axes.plot(np.sin, x_range=[-2 * np.pi, 2 * np.pi], color="#56B4E9", stroke_width=4.5)
        roots = VGroup(*[Dot(axes.c2p(k * np.pi, 0), radius=0.065, color="#F07B54") for k in range(-2, 3)])
        subtitle = Text("Preview rendered on the detected dark background", font_size=22, color="#CBD5E1").to_edge(DOWN, buff=0.25)
        self.add(heading, axes, curve, roots, subtitle)
