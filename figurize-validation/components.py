from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from manim import (
    Angle,
    Arrow,
    Axes,
    Circle,
    DashedLine,
    Dot,
    DoubleArrow,
    DOWN,
    LEFT,
    Line,
    MathTex,
    NumberLine,
    NumberPlane,
    ORIGIN,
    RIGHT,
    RoundedRectangle,
    Scene,
    Text,
    ThreeDScene,
    UP,
    VGroup,
)

from theme import (
    AXIS_PRIMARY,
    BACKGROUND_LIGHT,
    CAPTION_SIZE,
    CONSTRUCTION_AUXILIARY,
    EQUATION_SIZE,
    GRID_MAJOR,
    GRID_MINOR,
    LABEL_SIZE,
    POINT_ARBITRARY,
    POINT_CRITICAL,
    POINT_DEFAULT,
    POINT_HIGHLIGHT,
    PROJECTION_GUIDE,
    STROKE_AXIS,
    STROKE_EMPHASIZED,
    STROKE_NORMAL,
    STROKE_THIN,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TITLE_SIZE,
)


class FigurizeScene(Scene):
    """Base scene used by the validation gallery."""

    def setup(self):
        super().setup()
        self.camera.background_color = BACKGROUND_LIGHT


class FigurizeThreeDScene(ThreeDScene):
    """3D base scene with the same default background."""

    def setup(self):
        super().setup()
        self.camera.background_color = BACKGROUND_LIGHT


def title_group(title: str, subtitle: str | None = None) -> VGroup:
    title_mob = Text(title, font_size=TITLE_SIZE, color=TEXT_PRIMARY, weight="MEDIUM")
    if subtitle is None:
        return VGroup(title_mob)
    subtitle_mob = Text(subtitle, font_size=CAPTION_SIZE, color=TEXT_SECONDARY)
    return VGroup(title_mob, subtitle_mob).arrange(DOWN, buff=0.12)


def math_title(expression: str, subtitle: str | None = None) -> VGroup:
    equation = MathTex(expression, font_size=EQUATION_SIZE, color=TEXT_PRIMARY)
    if subtitle is None:
        return VGroup(equation)
    subtitle_mob = Text(subtitle, font_size=CAPTION_SIZE, color=TEXT_SECONDARY)
    return VGroup(equation, subtitle_mob).arrange(DOWN, buff=0.12)


def make_axes_2d(
    x_range: tuple[float, float, float] = (-4, 4, 1),
    y_range: tuple[float, float, float] = (-3, 3, 1),
    x_length: float = 9.5,
    y_length: float = 5.4,
    *,
    tips: bool = True,
    coordinates: bool = False,
) -> Axes:
    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        tips=tips,
        axis_config={
            "color": AXIS_PRIMARY,
            "stroke_width": STROKE_AXIS,
            "include_ticks": True,
            "tick_size": 0.055,
            "include_numbers": coordinates,
            "font_size": 22,
        },
    )
    return axes


def make_number_plane(
    x_range: tuple[float, float, float] = (-4, 4, 1),
    y_range: tuple[float, float, float] = (-3, 3, 1),
    x_length: float = 9.5,
    y_length: float = 5.4,
) -> NumberPlane:
    return NumberPlane(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        axis_config={"color": AXIS_PRIMARY, "stroke_width": STROKE_AXIS},
        background_line_style={
            "stroke_color": GRID_MAJOR,
            "stroke_width": 1.0,
            "stroke_opacity": 0.34,
        },
        faded_line_style={
            "stroke_color": GRID_MINOR,
            "stroke_width": 0.65,
            "stroke_opacity": 0.18,
        },
    )


def make_number_line(
    x_range: tuple[float, float, float] = (-4, 6, 1),
    length: float = 10.0,
    *,
    include_numbers: bool = True,
) -> NumberLine:
    return NumberLine(
        x_range=x_range,
        length=length,
        color=AXIS_PRIMARY,
        stroke_width=STROKE_AXIS,
        include_ticks=True,
        include_numbers=include_numbers,
        font_size=22,
        tip_width=0.18,
        tip_height=0.18,
    )


def point_marker(
    point: np.ndarray,
    role: str = "default",
    *,
    radius: float = 0.075,
) -> Dot:
    colors = {
        "default": POINT_DEFAULT,
        "highlight": POINT_HIGHLIGHT,
        "arbitrary": POINT_ARBITRARY,
        "critical": POINT_CRITICAL,
    }
    return Dot(point, radius=radius, color=colors.get(role, POINT_DEFAULT))


def open_point_marker(
    point: np.ndarray,
    *,
    color=POINT_DEFAULT,
    radius: float = 0.09,
    stroke_width: float = STROKE_EMPHASIZED,
) -> Circle:
    return Circle(
        radius=radius,
        color=color,
        stroke_width=stroke_width,
        fill_opacity=0,
    ).move_to(point)


def labeled_point(
    point: np.ndarray,
    label: str,
    *,
    role: str = "default",
    direction=UP + RIGHT,
    label_buff: float = 0.12,
    font_size: int = LABEL_SIZE,
) -> VGroup:
    marker = point_marker(point, role)
    label_mob = MathTex(label, font_size=font_size, color=TEXT_PRIMARY)
    label_mob.next_to(marker, direction, buff=label_buff)
    return VGroup(marker, label_mob)


def projection_guides(
    axes: Axes,
    x: float,
    y: float,
    *,
    x_label: str | None = None,
    y_label: str | None = None,
) -> VGroup:
    vertical = DashedLine(
        axes.c2p(x, 0),
        axes.c2p(x, y),
        dash_length=0.08,
        color=PROJECTION_GUIDE,
        stroke_width=STROKE_THIN,
    )
    horizontal = DashedLine(
        axes.c2p(0, y),
        axes.c2p(x, y),
        dash_length=0.08,
        color=PROJECTION_GUIDE,
        stroke_width=STROKE_THIN,
    )
    result = VGroup(vertical, horizontal)
    if x_label is not None:
        result.add(
            MathTex(x_label, font_size=22, color=TEXT_SECONDARY).next_to(
                axes.c2p(x, 0), DOWN, buff=0.1
            )
        )
    if y_label is not None:
        result.add(
            MathTex(y_label, font_size=22, color=TEXT_SECONDARY).next_to(
                axes.c2p(0, y), LEFT, buff=0.1
            )
        )
    return result


def dimension_marker(
    start: np.ndarray,
    end: np.ndarray,
    label: str,
    *,
    offset: np.ndarray = DOWN * 0.35,
) -> VGroup:
    arrow = DoubleArrow(
        start + offset,
        end + offset,
        buff=0,
        tip_length=0.15,
        color=CONSTRUCTION_AUXILIARY,
        stroke_width=STROKE_THIN,
    )
    label_mob = MathTex(label, font_size=LABEL_SIZE, color=TEXT_PRIMARY)
    label_mob.next_to(arrow, DOWN if offset[1] <= 0 else UP, buff=0.08)
    return VGroup(arrow, label_mob)


def distance_marker(
    start: np.ndarray,
    end: np.ndarray,
    label: str,
    *,
    label_direction=UP,
) -> VGroup:
    segment = Line(start, end, color=CONSTRUCTION_AUXILIARY, stroke_width=STROKE_THIN)
    ticks = VGroup()
    vector = end - start
    norm = np.linalg.norm(vector)
    if norm > 1e-8:
        normal = np.array([-vector[1], vector[0], 0.0]) / norm
        for point in (start, end):
            ticks.add(
                Line(
                    point - 0.09 * normal,
                    point + 0.09 * normal,
                    color=CONSTRUCTION_AUXILIARY,
                    stroke_width=STROKE_THIN,
                )
            )
    label_mob = MathTex(label, font_size=LABEL_SIZE, color=TEXT_PRIMARY)
    label_mob.next_to(segment.get_center(), label_direction, buff=0.12)
    return VGroup(segment, ticks, label_mob)


def angle_code(
    line_1: Line,
    line_2: Line,
    label: str | None = None,
    *,
    radius: float = 0.45,
    color=POINT_HIGHLIGHT,
) -> VGroup:
    angle = Angle(line_1, line_2, radius=radius, color=color, stroke_width=STROKE_NORMAL)
    result = VGroup(angle)
    if label is not None:
        label_mob = MathTex(label, font_size=LABEL_SIZE, color=TEXT_PRIMARY)
        label_mob.move_to(angle.point_from_proportion(0.5) + 0.18 * UP)
        result.add(label_mob)
    return result


def semantic_tick(
    axes: Axes,
    *,
    axis: str,
    value: float,
    label: str,
) -> VGroup:
    if axis == "x":
        center = axes.c2p(value, 0)
        tick = Line(center + 0.09 * UP, center + 0.09 * DOWN, color=AXIS_PRIMARY)
        label_mob = MathTex(label, font_size=22, color=TEXT_PRIMARY).next_to(tick, DOWN, buff=0.1)
    else:
        center = axes.c2p(0, value)
        tick = Line(center + 0.09 * LEFT, center + 0.09 * RIGHT, color=AXIS_PRIMARY)
        label_mob = MathTex(label, font_size=22, color=TEXT_PRIMARY).next_to(tick, LEFT, buff=0.1)
    return VGroup(tick, label_mob)


def vector_arrow(
    start: np.ndarray,
    end: np.ndarray,
    label: str | None = None,
    *,
    color=POINT_ARBITRARY,
) -> VGroup:
    arrow = Arrow(
        start,
        end,
        buff=0,
        color=color,
        stroke_width=STROKE_EMPHASIZED,
        max_tip_length_to_length_ratio=0.18,
    )
    result = VGroup(arrow)
    if label is not None:
        label_mob = MathTex(label, font_size=LABEL_SIZE, color=TEXT_PRIMARY)
        label_mob.next_to(arrow.get_end(), UP + RIGHT, buff=0.1)
        result.add(label_mob)
    return result


def legend(items: Iterable[tuple[str, object]]) -> VGroup:
    rows = VGroup()
    for label, color in items:
        swatch = Line(ORIGIN, RIGHT * 0.45, color=color, stroke_width=STROKE_EMPHASIZED)
        text = Text(label, font_size=20, color=TEXT_SECONDARY)
        rows.add(VGroup(swatch, text).arrange(RIGHT, buff=0.14))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    return rows


def component_card(title: str, body: VGroup, *, width: float = 3.2, height: float = 2.25) -> VGroup:
    card = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.16,
        color=GRID_MAJOR,
        stroke_width=1.2,
        fill_color=BACKGROUND_LIGHT,
        fill_opacity=1,
    )
    heading = Text(title, font_size=20, color=TEXT_SECONDARY, weight="MEDIUM")
    heading.next_to(card.get_top(), DOWN, buff=0.16)
    body.move_to(card.get_center() + DOWN * 0.12)
    return VGroup(card, heading, body)


def caption(text: str) -> Text:
    return Text(text, font_size=CAPTION_SIZE, color=TEXT_MUTED)
