from __future__ import annotations

import numpy as np
from manim import (
    Arrow3D,
    Circle,
    Cube,
    DashedLine,
    Dot,
    Dot3D,
    DOWN,
    LEFT,
    Line,
    Line3D,
    MathTex,
    ORIGIN,
    ParametricFunction,
    RIGHT,
    RoundedRectangle,
    Surface,
    TAU,
    Text,
    ThreeDAxes,
    UP,
    VGroup,
    DEGREES,
)

from components import (
    FigurizeScene,
    FigurizeThreeDScene,
    component_card,
    distance_marker,
    labeled_point,
    make_axes_2d,
    math_title,
    open_point_marker,
    point_marker,
    projection_guides,
    title_group,
    vector_arrow,
)
from theme import (
    AXIS_PRIMARY,
    BACKGROUND_LIGHT,
    CONSTRUCTION_AUXILIARY,
    FUNCTION_PRIMARY,
    FUNCTION_SECONDARY,
    GRID_MAJOR,
    LEVEL_CURVE_PRIMARY,
    POINT_ARBITRARY,
    POINT_CRITICAL,
    POINT_DEFAULT,
    POINT_HIGHLIGHT,
    PROJECTION_GUIDE,
    STROKE_EMPHASIZED,
    STROKE_NORMAL,
    STROKE_STRONG,
    STROKE_THIN,
    SURFACE_PRIMARY,
    SURFACE_SECONDARY,
    TANGENT_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    VECTOR_DEFAULT,
    VECTOR_HIGHLIGHT,
)


class PrimitiveComponents(FigurizeScene):
    def construct(self):
        heading = title_group(
            "Figurize primitive components",
            "Semantic roles remain stable even when a user changes the visual theme.",
        ).to_edge(UP, buff=0.28)

        markers = VGroup(
            point_marker(ORIGIN, "default"),
            point_marker(ORIGIN, "highlight"),
            point_marker(ORIGIN, "arbitrary"),
            open_point_marker(ORIGIN, color=POINT_DEFAULT),
        )
        labels = ["ordinary", "highlight", "arbitrary", "excluded"]
        marker_columns = VGroup()
        for marker, label in zip(markers, labels):
            text = Text(label, font_size=14, color=TEXT_MUTED)
            marker_columns.add(VGroup(marker, text).arrange(DOWN, buff=0.16))
        marker_columns.arrange(RIGHT, buff=0.33)
        points_card = component_card("Point markers", marker_columns, width=4.25, height=2.2)

        arrow = vector_arrow(LEFT * 1.0, RIGHT * 1.0, color=FUNCTION_PRIMARY)[0]
        solid = Line(LEFT * 1.0, RIGHT * 1.0, color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED)
        dashed = DashedLine(LEFT * 1.0, RIGHT * 1.0, color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_THIN)
        line_rows = VGroup(arrow, solid, dashed).arrange(DOWN, buff=0.34)
        lines_card = component_card("Lines and arrows", line_rows, width=4.25, height=2.2)

        triangle = VGroup(
            Line(LEFT * 0.95 + DOWN * 0.55, RIGHT * 0.35 + DOWN * 0.55, color=FUNCTION_PRIMARY),
            Line(RIGHT * 0.35 + DOWN * 0.55, LEFT * 0.35 + UP * 0.65, color=FUNCTION_PRIMARY),
            Line(LEFT * 0.35 + UP * 0.65, LEFT * 0.95 + DOWN * 0.55, color=FUNCTION_PRIMARY),
        )
        circle = Circle(radius=0.46, color=FUNCTION_SECONDARY, stroke_width=STROKE_NORMAL).shift(RIGHT * 0.72)
        arc = Circle(radius=0.5, color=POINT_HIGHLIGHT, stroke_width=STROKE_NORMAL).shift(LEFT * 0.65)
        arc.points = arc.points[: len(arc.points) // 3]
        shapes_card = component_card("Planar shapes", VGroup(triangle, circle, arc).scale(0.82), width=4.25, height=2.2)

        A = LEFT * 0.95 + DOWN * 0.35
        B = RIGHT * 0.95 + DOWN * 0.35
        C = LEFT * 0.35 + UP * 0.65
        rays = VGroup(Line(A, B, color=AXIS_PRIMARY), Line(A, C, color=AXIS_PRIMARY))
        angle_arc = Circle(radius=0.32, color=POINT_HIGHLIGHT, stroke_width=STROKE_NORMAL).move_to(A)
        angle_arc.points = angle_arc.points[: len(angle_arc.points) // 5]
        angle_label = MathTex(r"42^\circ", font_size=21, color=TEXT_PRIMARY).move_to(A + RIGHT * 0.54 + UP * 0.23)
        distance = Line(A + DOWN * 0.38, B + DOWN * 0.38, color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_THIN)
        distance_label = MathTex("d", font_size=22, color=TEXT_PRIMARY).next_to(distance, DOWN, buff=0.08)
        annotations_card = component_card(
            "Annotations",
            VGroup(rays, angle_arc, angle_label, distance, distance_label).scale(0.92),
            width=4.25,
            height=2.2,
        )

        cards = VGroup(points_card, lines_card, shapes_card, annotations_card)
        cards.arrange_in_grid(rows=2, cols=2, buff=(0.42, 0.38))
        cards.next_to(heading, DOWN, buff=0.34)
        self.add(heading, cards)


class CartesianComponents(FigurizeScene):
    def construct(self):
        heading = title_group(
            "Points, vectors and projections",
            "Numeric points, symbolic vectors and metric annotations share one frame.",
        ).to_edge(UP, buff=0.28)
        axes = make_axes_2d((-4, 4, 1), (-3, 3, 1), x_length=9.6, y_length=5.1)
        axes.next_to(heading, DOWN, buff=0.34)
        A = axes.c2p(2.1, 1.15)
        B = axes.c2p(-1.55, 2.0)
        guides = projection_guides(axes, 2.1, 1.15, x_label="2.1", y_label="1.15")
        metric = distance_marker(B, A, r"d(A,B)", label_direction=DOWN)
        metric[2].shift(DOWN * 0.02)
        vector = vector_arrow(axes.c2p(0, 0), axes.c2p(2.7, 2.15), r"\vec v")
        point_a = labeled_point(A, r"A(2.1,1.15)", role="highlight", direction=DOWN + RIGHT)
        point_b = labeled_point(B, r"B(-1.55,2)", role="arbitrary", direction=UP + LEFT)
        self.add(heading, axes, guides, metric, vector, point_a, point_b)


class FunctionRootsTangents(FigurizeScene):
    def construct(self):
        heading = math_title(
            r"f(x)=x^3-2x+1",
            "Roots, critical points and horizontal tangents in one reproducible layout",
        ).to_edge(UP, buff=0.25)
        axes = make_axes_2d((-3, 3, 1), (-5, 7, 1), x_length=8.7, y_length=5.15)
        axes.next_to(heading, DOWN, buff=0.3)
        curve = axes.plot(
            lambda x: x**3 - 2 * x + 1,
            x_range=[-2.25, 2.25],
            color=FUNCTION_PRIMARY,
            stroke_width=STROKE_STRONG,
        )
        roots = [(-1 - np.sqrt(5)) / 2, (-1 + np.sqrt(5)) / 2, 1.0]
        root_markers = VGroup(*[point_marker(axes.c2p(root, 0), "highlight") for root in roots])
        root_specs = [
            (roots[0], r"\frac{-1-\sqrt5}{2}", DOWN + LEFT, 0.16),
            (roots[1], r"\frac{-1+\sqrt5}{2}", DOWN + LEFT, 0.18),
            (roots[2], "1", DOWN + RIGHT, 0.16),
        ]
        root_labels = VGroup()
        for value, label, direction, buff in root_specs:
            label_mob = MathTex(label, font_size=19, color=TEXT_SECONDARY)
            label_mob.next_to(axes.c2p(value, 0), direction, buff=buff)
            root_labels.add(label_mob)

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

        legend_rows = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.4, color=FUNCTION_PRIMARY, stroke_width=STROKE_EMPHASIZED), Text("function", font_size=19, color=TEXT_SECONDARY)).arrange(RIGHT, buff=0.12),
            VGroup(Dot(radius=0.055, color=POINT_HIGHLIGHT), Text("roots", font_size=19, color=TEXT_SECONDARY)).arrange(RIGHT, buff=0.12),
            VGroup(Line(ORIGIN, RIGHT * 0.4, color=TANGENT_PRIMARY, stroke_width=STROKE_EMPHASIZED), Text("horizontal tangents", font_size=19, color=TEXT_SECONDARY)).arrange(RIGHT, buff=0.12),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        legend_rows.to_corner(UP + RIGHT, buff=0.35).shift(DOWN * 0.78)
        self.add(heading, axes, curve, tangents, root_markers, root_labels, critical_group, legend_rows)


class PointVectorSpace3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-2, 3, 1],
            x_length=5.8,
            y_length=5.8,
            z_length=4.1,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.8},
        )
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES, zoom=0.82)
        axes.shift(DOWN * 0.3)
        A_coords = (1.7, 1.15, 1.45)
        B_coords = (-1.2, 1.65, 0.45)
        A = Dot3D(axes.c2p(*A_coords), radius=0.085, color=POINT_HIGHLIGHT)
        B = Dot3D(axes.c2p(*B_coords), radius=0.085, color=POINT_ARBITRARY)
        vector = Arrow3D(
            start=axes.c2p(0, 0, 0),
            end=axes.c2p(1.8, -1.0, 1.6),
            color=VECTOR_DEFAULT,
            thickness=0.025,
            height=0.18,
            base_radius=0.07,
        )
        guides = VGroup(
            Line3D(axes.c2p(A_coords[0], 0, 0), axes.c2p(A_coords[0], A_coords[1], 0), color=PROJECTION_GUIDE, thickness=0.012),
            Line3D(axes.c2p(A_coords[0], A_coords[1], 0), axes.c2p(*A_coords), color=PROJECTION_GUIDE, thickness=0.012),
            Line3D(axes.c2p(0, 0, 0), axes.c2p(A_coords[0], 0, 0), color=PROJECTION_GUIDE, thickness=0.012),
        )
        title = Text("Points, vectors and projections in space", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.24)
        panel = RoundedRectangle(width=3.25, height=1.62, corner_radius=0.14, color=GRID_MAJOR, stroke_width=1.2, fill_color=BACKGROUND_LIGHT, fill_opacity=0.94)
        rows = VGroup(
            VGroup(Dot(radius=0.055, color=POINT_HIGHLIGHT), MathTex(r"A(1.7,1.15,1.45)", font_size=22, color=TEXT_PRIMARY)).arrange(RIGHT, buff=0.12),
            VGroup(Dot(radius=0.055, color=POINT_ARBITRARY), MathTex(r"B(-1.2,1.65,0.45)", font_size=22, color=TEXT_PRIMARY)).arrange(RIGHT, buff=0.12),
            VGroup(Line(ORIGIN, RIGHT * 0.38, color=VECTOR_DEFAULT, stroke_width=STROKE_EMPHASIZED), MathTex(r"\vec v", font_size=23, color=TEXT_PRIMARY)).arrange(RIGHT, buff=0.12),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows.move_to(panel)
        info = VGroup(panel, rows).to_corner(UP + RIGHT, buff=0.34).shift(DOWN * 0.62)
        self.add_fixed_in_frame_mobjects(title, info)
        self.add(axes, guides, A, B, vector)


class SolidGeometryCodes3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[0, 4, 1],
            x_length=5.2,
            y_length=5.2,
            z_length=3.8,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.5},
        )
        self.set_camera_orientation(phi=66 * DEGREES, theta=-48 * DEGREES, zoom=0.75)
        group = VGroup(axes)
        cube = Cube(side_length=2.2, fill_color=SURFACE_PRIMARY, fill_opacity=0.22, stroke_color=FUNCTION_PRIMARY, stroke_width=2.3)
        cube.move_to(axes.c2p(0.35, 0.2, 1.15))
        height = Line3D(axes.c2p(1.55, 1.3, 0.05), axes.c2p(1.55, 1.3, 2.25), color=VECTOR_HIGHLIGHT, thickness=0.018)
        diagonal = Line3D(axes.c2p(-0.75, -0.9, 0.05), axes.c2p(1.45, 1.3, 2.25), color=TANGENT_PRIMARY, thickness=0.018)
        group.add(cube, height, diagonal)
        group.shift(DOWN * 0.48)
        title = Text("Solid geometry: length, area and volume", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.24)
        panel = RoundedRectangle(width=2.35, height=1.55, corner_radius=0.14, color=GRID_MAJOR, stroke_width=1.2, fill_color=BACKGROUND_LIGHT, fill_opacity=0.94)
        rows = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.35, color=VECTOR_HIGHLIGHT, stroke_width=STROKE_EMPHASIZED), MathTex("h", font_size=24, color=TEXT_PRIMARY)).arrange(RIGHT, buff=0.12),
            VGroup(Line(ORIGIN, RIGHT * 0.35, color=TANGENT_PRIMARY, stroke_width=STROKE_EMPHASIZED), MathTex("d", font_size=24, color=TEXT_PRIMARY)).arrange(RIGHT, buff=0.12),
            MathTex(r"V=s^3", font_size=28, color=TEXT_PRIMARY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows.move_to(panel)
        info = VGroup(panel, rows).to_corner(DOWN + RIGHT, buff=0.38)
        self.add_fixed_in_frame_mobjects(title, info)
        self.add(group)


class SurfaceContours3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 3.5, 1],
            x_length=5.7,
            y_length=5.7,
            z_length=3.7,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.6},
        )
        self.set_camera_orientation(phi=67 * DEGREES, theta=-52 * DEGREES, zoom=0.72)
        surface = Surface(
            lambda u, v: axes.c2p(u, v, 0.42 * u**2 + 0.28 * v**2),
            u_range=[-1.85, 1.85],
            v_range=[-1.85, 1.85],
            resolution=(28, 28),
            checkerboard_colors=[SURFACE_PRIMARY, FUNCTION_PRIMARY],
            fill_opacity=0.72,
            stroke_width=0.3,
        )
        contours = VGroup()
        for z_value in (0.38, 0.85, 1.45):
            a = np.sqrt(z_value / 0.42)
            b = np.sqrt(z_value / 0.28)
            contours.add(
                ParametricFunction(
                    lambda t, aa=a, bb=b: axes.c2p(aa * np.cos(t), bb * np.sin(t), 0.04),
                    t_range=[0, TAU],
                    color=LEVEL_CURVE_PRIMARY,
                    stroke_width=STROKE_EMPHASIZED,
                )
            )
        group = VGroup(axes, surface, contours).shift(DOWN * 0.42)
        title = MathTex(r"f(x,y)=0.42x^2+0.28y^2", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.2)
        subtitle = Text("Surface with projected level curves", font_size=22, color=TEXT_SECONDARY).next_to(title, DOWN, buff=0.12)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.add(group)


class TangentPlaneSurface3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 3.5, 1],
            x_length=5.7,
            y_length=5.7,
            z_length=3.7,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.6},
        )
        self.set_camera_orientation(phi=67 * DEGREES, theta=-52 * DEGREES, zoom=0.7)
        f = lambda x, y: 0.45 * x**2 + 0.30 * y**2
        surface = Surface(
            lambda u, v: axes.c2p(u, v, f(u, v)),
            u_range=[-1.8, 1.8],
            v_range=[-1.8, 1.8],
            resolution=(28, 28),
            checkerboard_colors=[SURFACE_PRIMARY, FUNCTION_PRIMARY],
            fill_opacity=0.64,
            stroke_width=0.3,
        )
        x0, y0 = 0.85, 0.65
        z0 = f(x0, y0)
        fx = 0.9 * x0
        fy = 0.6 * y0
        tangent = Surface(
            lambda u, v: axes.c2p(u, v, z0 + fx * (u - x0) + fy * (v - y0)),
            u_range=[x0 - 0.82, x0 + 0.82],
            v_range=[y0 - 0.82, y0 + 0.82],
            resolution=(6, 6),
            checkerboard_colors=[SURFACE_SECONDARY, FUNCTION_SECONDARY],
            fill_opacity=0.62,
            stroke_color=FUNCTION_SECONDARY,
            stroke_width=0.65,
        )
        point = Dot3D(axes.c2p(x0, y0, z0), radius=0.095, color=POINT_HIGHLIGHT)
        normal_scale = 0.75
        normal = Arrow3D(
            start=axes.c2p(x0, y0, z0),
            end=axes.c2p(x0 - normal_scale * fx, y0 - normal_scale * fy, z0 + normal_scale),
            color=VECTOR_HIGHLIGHT,
            thickness=0.028,
            height=0.18,
            base_radius=0.07,
        )
        group = VGroup(axes, surface, tangent, point, normal).shift(DOWN * 0.38)
        title = Text("Surface, tangent plane and normal vector", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.22)
        formula = MathTex(
            r"T_A:\ z=f(A)+\nabla f(A)\cdot((x,y)-A)",
            font_size=27,
            color=TEXT_PRIMARY,
        ).to_edge(DOWN, buff=0.22)
        self.add_fixed_in_frame_mobjects(title, formula)
        self.add(group)
