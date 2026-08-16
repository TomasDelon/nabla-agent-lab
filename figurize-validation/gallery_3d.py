from __future__ import annotations

import numpy as np
from manim import (
    Arrow3D,
    Cube,
    Dot3D,
    Line3D,
    MathTex,
    ParametricFunction,
    Polygon,
    Surface,
    TAU,
    Text,
    ThreeDAxes,
    VGroup,
    DEGREES,
    DOWN,
    LEFT,
    RIGHT,
    UP,
)

from components import FigurizeThreeDScene
from theme import (
    AXIS_PRIMARY,
    CONSTRUCTION_AUXILIARY,
    FUNCTION_PRIMARY,
    FUNCTION_SECONDARY,
    LEVEL_CURVE_PRIMARY,
    POINT_ARBITRARY,
    POINT_HIGHLIGHT,
    PROJECTION_GUIDE,
    STROKE_EMPHASIZED,
    STROKE_NORMAL,
    STROKE_THIN,
    SURFACE_PRIMARY,
    SURFACE_SECONDARY,
    TANGENT_PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    VECTOR_DEFAULT,
    VECTOR_HIGHLIGHT,
)


class PointVectorSpace3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-2, 3, 1],
            x_length=6.2,
            y_length=6.2,
            z_length=4.4,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 2.0},
        )
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES, zoom=0.92)
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
        title = Text("Points, vectors and projections in space", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.25)
        labels = VGroup(
            MathTex(r"A(1.7,1.15,1.45)", font_size=24, color=TEXT_PRIMARY).to_corner(UP + RIGHT, buff=0.35).shift(DOWN * 0.65),
            MathTex(r"B(-1.2,1.65,0.45)", font_size=24, color=TEXT_SECONDARY).next_to(title, DOWN, buff=0.2),
            MathTex(r"\vec v", font_size=26, color=VECTOR_DEFAULT).to_corner(DOWN + RIGHT, buff=0.45),
        )
        self.add_fixed_in_frame_mobjects(title, labels)
        self.add(axes, guides, A, B, vector)


class SolidGeometryCodes3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[0, 4, 1],
            x_length=5.8,
            y_length=5.8,
            z_length=4.4,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.7},
        )
        self.set_camera_orientation(phi=66 * DEGREES, theta=-48 * DEGREES, zoom=0.9)
        cube = Cube(side_length=2.2, fill_color=SURFACE_PRIMARY, fill_opacity=0.2, stroke_color=FUNCTION_PRIMARY, stroke_width=2.4)
        cube.move_to(axes.c2p(0.35, 0.2, 1.15))
        height = Line3D(axes.c2p(1.55, 1.3, 0.05), axes.c2p(1.55, 1.3, 2.25), color=VECTOR_HIGHLIGHT, thickness=0.018)
        diagonal = Line3D(axes.c2p(-0.75, -0.9, 0.05), axes.c2p(1.45, 1.3, 2.25), color=TANGENT_PRIMARY, thickness=0.018)
        title = Text("Solid geometry: length, area and volume", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.25)
        formulas = VGroup(
            MathTex(r"h", font_size=26, color=VECTOR_HIGHLIGHT),
            MathTex(r"d", font_size=26, color=TANGENT_PRIMARY),
            MathTex(r"V=s^3", font_size=30, color=TEXT_PRIMARY),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT).to_corner(RIGHT + DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(title, formulas)
        self.add(axes, cube, height, diagonal)


class SurfaceContours3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 4, 1],
            x_length=6.2,
            y_length=6.2,
            z_length=4.5,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.8},
        )
        self.set_camera_orientation(phi=67 * DEGREES, theta=-52 * DEGREES, zoom=0.92)
        surface = Surface(
            lambda u, v: axes.c2p(u, v, 0.42 * u**2 + 0.28 * v**2),
            u_range=[-2.1, 2.1],
            v_range=[-2.1, 2.1],
            resolution=(28, 28),
            checkerboard_colors=[SURFACE_PRIMARY, FUNCTION_PRIMARY],
            fill_opacity=0.72,
            stroke_width=0.35,
        )
        contours = VGroup()
        for z_value, radius in [(0.45, 1.0), (1.05, 1.52), (1.85, 2.02)]:
            a = np.sqrt(z_value / 0.42)
            b = np.sqrt(z_value / 0.28)
            contours.add(
                ParametricFunction(
                    lambda t, aa=a, bb=b: axes.c2p(aa * np.cos(t), bb * np.sin(t), 0),
                    t_range=[0, TAU],
                    color=LEVEL_CURVE_PRIMARY,
                    stroke_width=STROKE_EMPHASIZED,
                )
            )
        title = MathTex(r"f(x,y)=0.42x^2+0.28y^2", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.25)
        subtitle = Text("Surface with projected level curves", font_size=22, color=TEXT_SECONDARY).next_to(title, DOWN, buff=0.15)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.add(axes, surface, contours)


class TangentPlaneSurface3D(FigurizeThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 4, 1],
            x_length=6.0,
            y_length=6.0,
            z_length=4.5,
            axis_config={"color": AXIS_PRIMARY, "stroke_width": 1.8},
        )
        self.set_camera_orientation(phi=67 * DEGREES, theta=-52 * DEGREES, zoom=0.9)
        f = lambda x, y: 0.45 * x**2 + 0.30 * y**2
        surface = Surface(
            lambda u, v: axes.c2p(u, v, f(u, v)),
            u_range=[-2.0, 2.0],
            v_range=[-2.0, 2.0],
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
            u_range=[x0 - 0.9, x0 + 0.9],
            v_range=[y0 - 0.9, y0 + 0.9],
            resolution=(6, 6),
            checkerboard_colors=[SURFACE_SECONDARY, FUNCTION_SECONDARY],
            fill_opacity=0.55,
            stroke_color=FUNCTION_SECONDARY,
            stroke_width=0.5,
        )
        point = Dot3D(axes.c2p(x0, y0, z0), radius=0.085, color=POINT_HIGHLIGHT)
        normal_scale = 0.9
        normal = Arrow3D(
            start=axes.c2p(x0, y0, z0),
            end=axes.c2p(x0 - normal_scale * fx, y0 - normal_scale * fy, z0 + normal_scale),
            color=VECTOR_HIGHLIGHT,
            thickness=0.025,
            height=0.18,
            base_radius=0.07,
        )
        title = Text("Surface, tangent plane and normal vector", font_size=34, color=TEXT_PRIMARY).to_edge(UP, buff=0.25)
        formula = MathTex(
            r"T_A:\ z=f(A)+\nabla f(A)\cdot((x,y)-A)",
            font_size=27,
            color=TEXT_PRIMARY,
        ).to_edge(DOWN, buff=0.25)
        self.add_fixed_in_frame_mobjects(title, formula)
        self.add(axes, surface, tangent, point, normal)
