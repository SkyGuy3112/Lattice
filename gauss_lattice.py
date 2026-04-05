from dataclasses import dataclass

from manimlib import *
import numpy as np


@dataclass
class GaussStyle:
    """Centralized visual and timing configuration for Gauss scenes."""
    camera_width: float = 24.0
    x_range: tuple = (-12, 12, 1)
    y_range: tuple = (-10, 14, 1)
    u_color: str = MAROON
    v_color: str = TEAL
    cell_color: str = YELLOW
    corner_buff: float = 0.35

    # Timings
    t_show_basis: float = 1.5
    t_show_cell: float = 1.2
    t_show_panels: float = 1.2
    t_step_box: float = 0.9
    t_wait: float = 1.0
    t_write_compute: float = 0.85
    t_write_done: float = 0.8
    t_fade_compute_done: float = 0.5
    t_write_update_shift: float = 1.0
    t_basis_replace: float = 1.1
    t_write_swap: float = 0.7
    t_swap_replace: float = 1.0
    t_fade_swap: float = 0.4
    t_fade_compute_update: float = 0.4
    t_table_replace: float = 0.8
    t_final: float = 1.0
    t_end_wait: float = 2.0


class GaussMath:
    """Pure helper utilities for rounding and vector text formatting."""
    @staticmethod
    def nearest_integer_ties_toward_zero(x):
        lower = int(np.floor(x))
        upper = int(np.ceil(x))
        d_lower = abs(x - lower)
        d_upper = abs(x - upper)
        if d_lower < d_upper:
            return lower
        if d_upper < d_lower:
            return upper
        return lower if abs(lower) <= abs(upper) else upper

    @staticmethod
    def vec_tex(name, vec):
        return f"{name}=({int(vec[0])},{int(vec[1])})"

    @staticmethod
    def vec_pair(vec):
        return f"({int(round(vec[0]))},{int(round(vec[1]))})"


class GaussAlgorithmState:
    """Mutable state machine for one Gauss reduction run."""
    def __init__(self, u_init, v_init, max_iterations=10):
        self.u = np.array(u_init, dtype=float)
        self.v = np.array(v_init, dtype=float)
        self.c = 1
        self.max_iterations = max_iterations
        self.iteration = 0

    def should_continue(self):
        return self.c != 0 and self.iteration < self.max_iterations

    def begin_iteration(self):
        self.iteration += 1

    def compute(self):
        mu = float(np.dot(self.u, self.v) / np.dot(self.u, self.u))
        c = GaussMath.nearest_integer_ties_toward_zero(mu)
        v_minus_cu = self.v - c * self.u
        self.c = c
        return mu, c, v_minus_cu

    def apply_v_update(self, new_v):
        self.v = new_v.copy()

    def maybe_swap(self):
        if np.linalg.norm(self.u) > np.linalg.norm(self.v):
            self.u, self.v = self.v.copy(), self.u.copy()
            return True
        return False


class GaussVisualBuilder:
    """Builds Manim mobjects for vectors, panels, status text, and table."""
    def __init__(self, scene, plane, style):
        self.scene = scene
        self.plane = plane
        self.style = style
        self.origin = plane.c2p(0, 0)

    def c2p(self, vec):
        return self.plane.c2p(vec[0], vec[1])

    def build_basis_group(self, u, v):
        u_arrow = Arrow(self.origin, self.c2p(u), buff=0, color=self.style.u_color)
        u_arrow.set_stroke(self.style.u_color, width=4, opacity=1.0)

        v_arrow = Arrow(self.origin, self.c2p(v), buff=0, color=self.style.v_color)
        v_arrow.set_stroke(self.style.v_color, width=4, opacity=1.0)

        u_label = Tex("u").set_color(self.style.u_color).next_to(u_arrow.get_end(), RIGHT + DOWN, buff=0.08)
        v_label = Tex("v").set_color(self.style.v_color).next_to(v_arrow.get_end(), LEFT + UP, buff=0.08)
        return VGroup(u_arrow, v_arrow, u_label, v_label)

    def build_cell_group(self, u, v):
        p0 = self.origin
        p1 = self.c2p(u)
        p2 = self.c2p(u + v)
        p3 = self.c2p(v)

        fill = Polygon(p0, p1, p2, p3, stroke_width=0)
        fill.set_fill(self.style.cell_color, opacity=0.12)

        edges = VGroup(
            DashedLine(p0, p1, color=self.style.cell_color, stroke_width=2.6),
            DashedLine(p1, p2, color=self.style.cell_color, stroke_width=2.6),
            DashedLine(p2, p3, color=self.style.cell_color, stroke_width=2.6),
            DashedLine(p3, p0, color=self.style.cell_color, stroke_width=2.6),
        )
        return VGroup(fill, edges)

    def build_status_block(self, u, v):
        nu = np.linalg.norm(u)
        nv = np.linalg.norm(v)
        lines = VGroup(
            Tex(GaussMath.vec_tex("u", u)).set_color(self.style.u_color),
            Tex(GaussMath.vec_tex("v", v)).set_color(self.style.v_color),
            Tex(rf"\lVert u\rVert={nu:.3f}").set_color(WHITE),
            Tex(rf"\lVert v\rVert={nv:.3f}").set_color(WHITE),
        )
        return lines.arrange(DOWN, aligned_edge=LEFT, buff=0.14)

    def build_algorithm_panel(self):
        line1 = Tex(r"\text{Input: basis }[u,v]\text{ of }L\subseteq\mathbb{Z}^2,\ \lVert u\rVert\leq\lVert v\rVert")
        line2 = Tex(r"\text{Output: reduced basis }[u,v]")
        line3 = Tex(r"1.\ c\leftarrow 1")
        line4 = Tex(r"2.\ \text{while }c\neq 0\ \text{do}")
        line5 = Tex(r"\ \ (a)\ \mu=\langle u,v\rangle/\lVert u\rVert^2,\ c=[\mu]")
        line6 = Tex(r"\ \ (b)\ v\leftarrow v-cu")
        line7 = Tex(r"\ \ (c)\ \text{if }\lVert u\rVert>\lVert v\rVert\ \text{then swap }u,v")
        line8 = Tex(r"3.\ \text{return }[u,v]")

        lines = VGroup(line1, line2, line3, line4, line5, line6, line7, line8)
        for ln in lines:
            ln.set_color(WHITE)
            ln.scale(0.60)

        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        frame = SurroundingRectangle(lines, color=GREY_B, buff=0.18)
        panel = VGroup(frame, lines)
        return panel, lines

    def build_history_table(self, rows):
        headers = [
            r"u",
            r"\lVert u\rVert^2",
            r"v",
            r"\lVert v\rVert^2",
            r"c",
            r"v-cu",
        ]

        col_widths = [2.0, 1.8, 2.0, 1.8, 0.8, 2.2]
        row_height = 0.60
        total_rows = 1 + len(rows)

        table_width = sum(col_widths)
        table_height = row_height * total_rows

        outer = Rectangle(width=table_width, height=table_height)
        outer.set_stroke(color=GREY_B, width=2.8, opacity=1.0)
        outer.set_fill(BLACK, opacity=0.25)

        x_left = -table_width / 2
        y_top = table_height / 2

        inner_vertical = VGroup()
        x_cursor = x_left
        for width in col_widths[:-1]:
            x_cursor += width
            vline = Line(
                np.array([x_cursor, -table_height / 2, 0.0]),
                np.array([x_cursor, table_height / 2, 0.0]),
            )
            vline.set_stroke(color=GREY_B, width=1.2, opacity=0.95)
            inner_vertical.add(vline)

        inner_horizontal = VGroup()
        for ridx in range(1, total_rows):
            y = y_top - ridx * row_height
            hline = Line(
                np.array([-table_width / 2, y, 0.0]),
                np.array([table_width / 2, y, 0.0]),
            )
            hline.set_stroke(color=GREY_B, width=1.2, opacity=0.95)
            inner_horizontal.add(hline)

        entries = VGroup()
        x_cursor = x_left
        for cidx, width in enumerate(col_widths):
            x_center = x_cursor + width / 2
            x_cursor += width

            col_entries = [headers[cidx]] + [row[cidx] for row in rows]
            for ridx, entry in enumerate(col_entries):
                y_center = y_top - (ridx + 0.5) * row_height
                mob = Tex(entry)
                mob.scale(0.56 if ridx == 0 else 0.52)
                mob.set_color(YELLOW if ridx == 0 else WHITE)
                mob.move_to(np.array([x_center, y_center, 0.0]))
                entries.add(mob)

        return VGroup(outer, inner_vertical, inner_horizontal, entries)


class GaussLayout:
    """Applies corner-based positioning rules for scene UI blocks."""
    def __init__(self, scene, style):
        self.scene = scene
        self.style = style

    def pin_status_block(self, block):
        block.next_to(self.scene.camera.frame.get_corner(UL), RIGHT + DOWN, buff=self.style.corner_buff)
        return block

    def pin_algorithm_panel(self, panel):
        panel.next_to(self.scene.camera.frame.get_corner(UR), LEFT + DOWN, buff=self.style.corner_buff)
        return panel

    def pin_history_table(self, table):
        table.next_to(self.scene.camera.frame.get_corner(DL), RIGHT + UP, buff=self.style.corner_buff)
        return table


class BaseGaussReductionScene(Scene):
    """Shared scene orchestration for Gauss reduction animation variants."""
    enable_table = False

    def construct(self):
        style = GaussStyle()
        self.camera.background_color = BLACK
        self.camera.frame.set_width(style.camera_width)

        plane = NumberPlane(
            x_range=style.x_range,
            y_range=style.y_range,
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1.15,
                "stroke_opacity": 0.28,
            },
            axis_config={
                "stroke_color": GREY,
                "stroke_width": 1.8,
                "stroke_opacity": 0.45,
            },
        )

        algo = GaussAlgorithmState((3.0, 5.0), (4.0, 7.0), max_iterations=10)
        builder = GaussVisualBuilder(self, plane, style)
        layout = GaussLayout(self, style)

        basis_group = builder.build_basis_group(algo.u, algo.v)
        cell_group = builder.build_cell_group(algo.u, algo.v)
        status_block = layout.pin_status_block(builder.build_status_block(algo.u, algo.v))
        panel, lines = builder.build_algorithm_panel()
        panel = layout.pin_algorithm_panel(panel)
        step_box = SurroundingRectangle(lines[2], color=YELLOW, buff=0.06)

        history_rows = []
        history_table = None
        if self.enable_table:
            history_table = layout.pin_history_table(builder.build_history_table(history_rows))

        self.add(plane)
        self.play(
            ShowCreation(basis_group[0]),
            ShowCreation(basis_group[1]),
            Write(basis_group[2]),
            Write(basis_group[3]),
            run_time=style.t_show_basis,
        )
        self.play(FadeIn(cell_group[0]), ShowCreation(cell_group[1]), run_time=style.t_show_cell)
        init_anims = [FadeIn(panel), Write(status_block), ShowCreation(step_box)]
        if self.enable_table:
            init_anims.append(FadeIn(history_table))
        self.play(*init_anims, run_time=style.t_show_panels)
        self.wait(style.t_wait)

        while algo.should_continue():
            algo.begin_iteration()

            new_step_box = SurroundingRectangle(lines[4], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=style.t_step_box)
            step_box = new_step_box
            self.wait(style.t_wait)

            mu, c, v_minus_cu = algo.compute()
            pending_row = (
                GaussMath.vec_pair(algo.u),
                f"{int(round(np.dot(algo.u, algo.u)))}",
                GaussMath.vec_pair(algo.v),
                f"{int(round(np.dot(algo.v, algo.v)))}",
                f"{c}",
                GaussMath.vec_pair(v_minus_cu),
            )

            compute_text = Tex(
                rf"\mu=\langle u,v\rangle/\lVert u\rVert^2={mu:.4f},\quad c=[\mu]={c}"
            )
            compute_text.set_color(WHITE)
            compute_text.scale(0.74)
            compute_text.next_to(status_block, DOWN, aligned_edge=LEFT, buff=0.28)
            self.play(Write(compute_text), run_time=style.t_write_compute)
            self.wait(style.t_wait)

            if c == 0:
                done_text = Tex(r"c=0,\ \text{stop the loop}")
                done_text.set_color(WHITE)
                done_text.scale(0.74)
                done_text.next_to(compute_text, DOWN, aligned_edge=LEFT, buff=0.18)
                new_step_box = SurroundingRectangle(lines[7], color=GREEN, buff=0.06)
                self.play(
                    Write(done_text),
                    ReplacementTransform(step_box, new_step_box),
                    run_time=style.t_write_done,
                )
                step_box = new_step_box
                self.wait(style.t_wait)
                self.play(FadeOut(done_text), FadeOut(compute_text), run_time=style.t_fade_compute_done)

                if self.enable_table:
                    history_rows.append(pending_row)
                    new_history_table = layout.pin_history_table(builder.build_history_table(history_rows))
                    self.play(ReplacementTransform(history_table, new_history_table), run_time=style.t_table_replace)
                    history_table = new_history_table
                    self.wait(style.t_wait)
                break

            new_step_box = SurroundingRectangle(lines[5], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=style.t_step_box)
            step_box = new_step_box
            self.wait(style.t_wait)

            old_v = algo.v.copy()
            new_v = v_minus_cu

            update_text = Tex(rf"v\leftarrow v-{c}u=({int(new_v[0])},{int(new_v[1])})")
            update_text.set_color(WHITE)
            update_text.scale(0.74)
            update_text.next_to(compute_text, DOWN, aligned_edge=LEFT, buff=0.18)

            shift_arrow = Arrow(builder.c2p(old_v), builder.c2p(new_v), buff=0, color=RED)
            shift_arrow.set_stroke(RED, width=3.2, opacity=1.0)
            self.play(Write(update_text), ShowCreation(shift_arrow), run_time=style.t_write_update_shift)
            self.wait(style.t_wait)

            algo.apply_v_update(new_v)
            new_basis = builder.build_basis_group(algo.u, algo.v)
            new_cell = builder.build_cell_group(algo.u, algo.v)
            new_status = layout.pin_status_block(builder.build_status_block(algo.u, algo.v))

            self.play(
                ReplacementTransform(basis_group, new_basis),
                ReplacementTransform(cell_group, new_cell),
                ReplacementTransform(status_block, new_status),
                FadeOut(shift_arrow),
                run_time=style.t_basis_replace,
            )
            self.wait(style.t_wait)
            basis_group = new_basis
            cell_group = new_cell
            status_block = new_status

            new_step_box = SurroundingRectangle(lines[6], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=style.t_step_box)
            step_box = new_step_box
            self.wait(style.t_wait)

            swapped = algo.maybe_swap()
            if swapped:
                swap_text = Tex(r"\lVert u\rVert>\lVert v\rVert,\ \text{swap }u\ \text{and }v")
                swap_text.set_color(WHITE)
                swap_text.scale(0.74)
                swap_text.next_to(update_text, DOWN, aligned_edge=LEFT, buff=0.18)
                self.play(Write(swap_text), run_time=style.t_write_swap)

                new_basis = builder.build_basis_group(algo.u, algo.v)
                new_cell = builder.build_cell_group(algo.u, algo.v)
                new_status = layout.pin_status_block(builder.build_status_block(algo.u, algo.v))

                self.play(
                    ReplacementTransform(basis_group, new_basis),
                    ReplacementTransform(cell_group, new_cell),
                    ReplacementTransform(status_block, new_status),
                    run_time=style.t_swap_replace,
                )
                self.wait(style.t_wait)
                basis_group = new_basis
                cell_group = new_cell
                status_block = new_status
                self.play(FadeOut(swap_text), run_time=style.t_fade_swap)

            self.play(FadeOut(compute_text), FadeOut(update_text), run_time=style.t_fade_compute_update)

            if self.enable_table:
                history_rows.append(pending_row)
                new_history_table = layout.pin_history_table(builder.build_history_table(history_rows))
                self.play(ReplacementTransform(history_table, new_history_table), run_time=style.t_table_replace)
                history_table = new_history_table
            self.wait(style.t_wait)

        final_box = SurroundingRectangle(status_block, color=GREEN, buff=0.12)
        final_text = Text("Returned reduced basis [u, v]", font_size=30, color=GREEN)
        final_text.next_to(final_box, DOWN, buff=0.25)

        self.play(ShowCreation(final_box), Write(final_text), run_time=style.t_final)
        self.wait(style.t_end_wait)


class GaussLatticeReduction(BaseGaussReductionScene):
    """Gauss reduction scene without the iteration history table."""
    enable_table = False


class GaussLatticeReductionWithTable(BaseGaussReductionScene):
    """Gauss reduction scene with a bottom-left growing history table."""
    enable_table = True
