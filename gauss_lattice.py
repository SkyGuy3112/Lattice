from manimlib import *
import numpy as np


class GaussLatticeReduction(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        self.camera.frame.set_width(24.0)

        plane = NumberPlane(
            x_range=(-12, 12, 1),
            y_range=(-10, 14, 1),
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

        origin = plane.c2p(0, 0)
        u_color = MAROON
        v_color = TEAL
        cell_color = YELLOW

        def c2p(vec):
            return plane.c2p(vec[0], vec[1])

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

        def vec_tex(name, vec):
            return f"{name}=({int(vec[0])},{int(vec[1])})"

        def build_basis_group(u, v):
            u_arrow = Arrow(origin, c2p(u), buff=0, color=u_color)
            u_arrow.set_stroke(u_color, width=4, opacity=1.0)

            v_arrow = Arrow(origin, c2p(v), buff=0, color=v_color)
            v_arrow.set_stroke(v_color, width=4, opacity=1.0)

            u_label = Tex("u").set_color(u_color).next_to(u_arrow.get_end(), RIGHT + DOWN, buff=0.08)
            v_label = Tex("v").set_color(v_color).next_to(v_arrow.get_end(), LEFT + UP, buff=0.08)
            return VGroup(u_arrow, v_arrow, u_label, v_label)

        def build_cell_group(u, v):
            p0 = origin
            p1 = c2p(u)
            p2 = c2p(u + v)
            p3 = c2p(v)

            fill = Polygon(p0, p1, p2, p3, stroke_width=0)
            fill.set_fill(cell_color, opacity=0.12)

            edges = VGroup(
                DashedLine(p0, p1, color=cell_color, stroke_width=2.6),
                DashedLine(p1, p2, color=cell_color, stroke_width=2.6),
                DashedLine(p2, p3, color=cell_color, stroke_width=2.6),
                DashedLine(p3, p0, color=cell_color, stroke_width=2.6),
            )
            return VGroup(fill, edges)

        def build_status_block(u, v):
            nu = np.linalg.norm(u)
            nv = np.linalg.norm(v)
            lines = VGroup(
                Tex(vec_tex("u", u)).set_color(u_color),
                Tex(vec_tex("v", v)).set_color(v_color),
                Tex(rf"\lVert u\rVert={nu:.3f}").set_color(WHITE),
                Tex(rf"\lVert v\rVert={nv:.3f}").set_color(WHITE),
            )
            return lines.arrange(DOWN, aligned_edge=LEFT, buff=0.14)

        def build_algorithm_panel():
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

        def pin_status_block(block):
            block.next_to(self.camera.frame.get_corner(UL), RIGHT + DOWN, buff=0.35)
            return block

        def pin_algorithm_panel(panel):
            panel.next_to(self.camera.frame.get_corner(UR), LEFT + DOWN, buff=0.35)
            return panel

        u = np.array([3.0, 5.0])
        v = np.array([4.0, 7.0])
        c = 1

        basis_group = build_basis_group(u, v)
        cell_group = build_cell_group(u, v)
        status_block = pin_status_block(build_status_block(u, v))
        panel, lines = build_algorithm_panel()
        panel = pin_algorithm_panel(panel)
        step_box = SurroundingRectangle(lines[2], color=YELLOW, buff=0.06)

        self.add(plane)
        self.play(ShowCreation(basis_group[0]), ShowCreation(basis_group[1]), Write(basis_group[2]), Write(basis_group[3]), run_time=1.5)
        self.play(FadeIn(cell_group[0]), ShowCreation(cell_group[1]), run_time=1.2)
        self.play(FadeIn(panel), Write(status_block), ShowCreation(step_box), run_time=1.2)
        self.wait(1.0)

        iteration = 0
        max_iterations = 10

        while c != 0 and iteration < max_iterations:
            iteration += 1

            new_step_box = SurroundingRectangle(lines[4], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=0.9)
            step_box = new_step_box
            self.wait(1.0)

            mu = float(np.dot(u, v) / np.dot(u, u))
            c = nearest_integer_ties_toward_zero(mu)

            compute_text = Tex(
                rf"\mu=\langle u,v\rangle/\lVert u\rVert^2={mu:.4f},\quad c=[\mu]={c}"
            )
            compute_text.set_color(WHITE)
            compute_text.scale(0.74)
            compute_text.next_to(status_block, DOWN, aligned_edge=LEFT, buff=0.28)
            self.play(Write(compute_text), run_time=0.85)
            self.wait(1.0)

            if c == 0:
                done_text = Tex(r"c=0,\ \text{stop the loop}")
                done_text.set_color(WHITE)
                done_text.scale(0.74)
                done_text.next_to(compute_text, DOWN, aligned_edge=LEFT, buff=0.18)
                new_step_box = SurroundingRectangle(lines[7], color=GREEN, buff=0.06)
                self.play(Write(done_text), ReplacementTransform(step_box, new_step_box), run_time=0.8)
                step_box = new_step_box
                self.wait(1.0)
                self.play(FadeOut(done_text), FadeOut(compute_text), run_time=0.5)
                break

            new_step_box = SurroundingRectangle(lines[5], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=0.9)
            step_box = new_step_box
            self.wait(1.0)

            old_v = v.copy()
            new_v = v - c * u

            update_text = Tex(rf"v\leftarrow v-{c}u=({int(new_v[0])},{int(new_v[1])})")
            update_text.set_color(WHITE)
            update_text.scale(0.74)
            update_text.next_to(compute_text, DOWN, aligned_edge=LEFT, buff=0.18)

            shift_arrow = Arrow(c2p(old_v), c2p(new_v), buff=0, color=RED)
            shift_arrow.set_stroke(RED, width=3.2, opacity=1.0)
            self.play(Write(update_text), ShowCreation(shift_arrow), run_time=1.0)
            self.wait(1.0)

            v = new_v
            new_basis = build_basis_group(u, v)
            new_cell = build_cell_group(u, v)
            new_status = pin_status_block(build_status_block(u, v))

            self.play(
                ReplacementTransform(basis_group, new_basis),
                ReplacementTransform(cell_group, new_cell),
                ReplacementTransform(status_block, new_status),
                FadeOut(shift_arrow),
                run_time=1.1,
            )
            self.wait(1.0)
            basis_group = new_basis
            cell_group = new_cell
            status_block = new_status

            new_step_box = SurroundingRectangle(lines[6], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=0.9)
            step_box = new_step_box
            self.wait(1.0)

            if np.linalg.norm(u) > np.linalg.norm(v):
                swap_text = Tex(r"\lVert u\rVert>\lVert v\rVert,\ \text{swap }u\ \text{and }v")
                swap_text.set_color(WHITE)
                swap_text.scale(0.74)
                swap_text.next_to(update_text, DOWN, aligned_edge=LEFT, buff=0.18)
                self.play(Write(swap_text), run_time=0.7)

                u, v = v.copy(), u.copy()
                new_basis = build_basis_group(u, v)
                new_cell = build_cell_group(u, v)
                new_status = pin_status_block(build_status_block(u, v))

                self.play(
                    ReplacementTransform(basis_group, new_basis),
                    ReplacementTransform(cell_group, new_cell),
                    ReplacementTransform(status_block, new_status),
                    run_time=1.0,
                )
                self.wait(1.0)
                basis_group = new_basis
                cell_group = new_cell
                status_block = new_status
                self.play(FadeOut(swap_text), run_time=0.4)

            self.play(FadeOut(compute_text), FadeOut(update_text), run_time=0.4)
            self.wait(1.0)

        final_box = SurroundingRectangle(status_block, color=GREEN, buff=0.12)
        final_text = Text("Returned reduced basis [u, v]", font_size=30, color=GREEN)
        final_text.next_to(final_box, DOWN, buff=0.25)

        self.play(ShowCreation(final_box), Write(final_text), run_time=1.0)
        self.wait(2.0)


class GaussLatticeReductionWithTable(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        self.camera.frame.set_width(24.0)

        plane = NumberPlane(
            x_range=(-12, 12, 1),
            y_range=(-10, 14, 1),
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

        origin = plane.c2p(0, 0)
        u_color = MAROON
        v_color = TEAL
        cell_color = YELLOW

        def c2p(vec):
            return plane.c2p(vec[0], vec[1])

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

        def vec_tex(name, vec):
            return f"{name}=({int(vec[0])},{int(vec[1])})"

        def vec_pair(vec):
            return f"({int(round(vec[0]))},{int(round(vec[1]))})"

        def build_basis_group(u, v):
            u_arrow = Arrow(origin, c2p(u), buff=0, color=u_color)
            u_arrow.set_stroke(u_color, width=4, opacity=1.0)

            v_arrow = Arrow(origin, c2p(v), buff=0, color=v_color)
            v_arrow.set_stroke(v_color, width=4, opacity=1.0)

            u_label = Tex("u").set_color(u_color).next_to(u_arrow.get_end(), RIGHT + DOWN, buff=0.08)
            v_label = Tex("v").set_color(v_color).next_to(v_arrow.get_end(), LEFT + UP, buff=0.08)
            return VGroup(u_arrow, v_arrow, u_label, v_label)

        def build_cell_group(u, v):
            p0 = origin
            p1 = c2p(u)
            p2 = c2p(u + v)
            p3 = c2p(v)

            fill = Polygon(p0, p1, p2, p3, stroke_width=0)
            fill.set_fill(cell_color, opacity=0.12)

            edges = VGroup(
                DashedLine(p0, p1, color=cell_color, stroke_width=2.6),
                DashedLine(p1, p2, color=cell_color, stroke_width=2.6),
                DashedLine(p2, p3, color=cell_color, stroke_width=2.6),
                DashedLine(p3, p0, color=cell_color, stroke_width=2.6),
            )
            return VGroup(fill, edges)

        def build_status_block(u, v):
            nu = np.linalg.norm(u)
            nv = np.linalg.norm(v)
            lines = VGroup(
                Tex(vec_tex("u", u)).set_color(u_color),
                Tex(vec_tex("v", v)).set_color(v_color),
                Tex(rf"\lVert u\rVert={nu:.3f}").set_color(WHITE),
                Tex(rf"\lVert v\rVert={nv:.3f}").set_color(WHITE),
            )
            return lines.arrange(DOWN, aligned_edge=LEFT, buff=0.14)

        def build_algorithm_panel():
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

        def build_history_table(rows):
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
            total_rows = 1 + len(rows)  # header + data rows

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

        def pin_status_block(block):
            block.next_to(self.camera.frame.get_corner(UL), RIGHT + DOWN, buff=0.35)
            return block

        def pin_algorithm_panel(panel):
            panel.next_to(self.camera.frame.get_corner(UR), LEFT + DOWN, buff=0.35)
            return panel

        def pin_history_table(table):
            table.next_to(self.camera.frame.get_corner(DL), RIGHT + UP, buff=0.35)
            return table

        u = np.array([3.0, 5.0])
        v = np.array([4.0, 7.0])
        c = 1
        history_rows = []

        basis_group = build_basis_group(u, v)
        cell_group = build_cell_group(u, v)
        status_block = pin_status_block(build_status_block(u, v))
        panel, lines = build_algorithm_panel()
        panel = pin_algorithm_panel(panel)
        step_box = SurroundingRectangle(lines[2], color=YELLOW, buff=0.06)
        history_table = pin_history_table(build_history_table(history_rows))

        self.add(plane)
        self.play(ShowCreation(basis_group[0]), ShowCreation(basis_group[1]), Write(basis_group[2]), Write(basis_group[3]), run_time=1.5)
        self.play(FadeIn(cell_group[0]), ShowCreation(cell_group[1]), run_time=1.2)
        self.play(FadeIn(panel), Write(status_block), ShowCreation(step_box), FadeIn(history_table), run_time=1.2)
        self.wait(1.0)

        iteration = 0
        max_iterations = 10

        while c != 0 and iteration < max_iterations:
            iteration += 1

            new_step_box = SurroundingRectangle(lines[4], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=0.9)
            step_box = new_step_box
            self.wait(1.0)

            mu = float(np.dot(u, v) / np.dot(u, u))
            c = nearest_integer_ties_toward_zero(mu)
            v_minus_cu = v - c * u
            pending_row = (
                vec_pair(u),
                f"{int(round(np.dot(u, u)))}",
                vec_pair(v),
                f"{int(round(np.dot(v, v)))}",
                f"{c}",
                vec_pair(v_minus_cu),
            )

            compute_text = Tex(
                rf"\mu=\langle u,v\rangle/\lVert u\rVert^2={mu:.4f},\quad c=[\mu]={c}"
            )
            compute_text.set_color(WHITE)
            compute_text.scale(0.74)
            compute_text.next_to(status_block, DOWN, aligned_edge=LEFT, buff=0.28)
            self.play(Write(compute_text), run_time=0.85)
            self.wait(1.0)

            if c == 0:
                done_text = Tex(r"c=0,\ \text{stop the loop}")
                done_text.set_color(WHITE)
                done_text.scale(0.74)
                done_text.next_to(compute_text, DOWN, aligned_edge=LEFT, buff=0.18)
                new_step_box = SurroundingRectangle(lines[7], color=GREEN, buff=0.06)
                self.play(Write(done_text), ReplacementTransform(step_box, new_step_box), run_time=0.8)
                step_box = new_step_box
                self.wait(1.0)
                self.play(FadeOut(done_text), FadeOut(compute_text), run_time=0.5)

                history_rows.append(pending_row)
                new_history_table = pin_history_table(build_history_table(history_rows))
                self.play(ReplacementTransform(history_table, new_history_table), run_time=0.8)
                history_table = new_history_table
                self.wait(1.0)
                break

            new_step_box = SurroundingRectangle(lines[5], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=0.9)
            step_box = new_step_box
            self.wait(1.0)

            old_v = v.copy()
            new_v = v_minus_cu

            update_text = Tex(rf"v\leftarrow v-{c}u=({int(new_v[0])},{int(new_v[1])})")
            update_text.set_color(WHITE)
            update_text.scale(0.74)
            update_text.next_to(compute_text, DOWN, aligned_edge=LEFT, buff=0.18)

            shift_arrow = Arrow(c2p(old_v), c2p(new_v), buff=0, color=RED)
            shift_arrow.set_stroke(RED, width=3.2, opacity=1.0)
            self.play(Write(update_text), ShowCreation(shift_arrow), run_time=1.0)
            self.wait(1.0)

            v = new_v
            new_basis = build_basis_group(u, v)
            new_cell = build_cell_group(u, v)
            new_status = pin_status_block(build_status_block(u, v))

            self.play(
                ReplacementTransform(basis_group, new_basis),
                ReplacementTransform(cell_group, new_cell),
                ReplacementTransform(status_block, new_status),
                FadeOut(shift_arrow),
                run_time=1.1,
            )
            self.wait(1.0)
            basis_group = new_basis
            cell_group = new_cell
            status_block = new_status

            new_step_box = SurroundingRectangle(lines[6], color=YELLOW, buff=0.06)
            self.play(ReplacementTransform(step_box, new_step_box), run_time=0.9)
            step_box = new_step_box
            self.wait(1.0)

            if np.linalg.norm(u) > np.linalg.norm(v):
                swap_text = Tex(r"\lVert u\rVert>\lVert v\rVert,\ \text{swap }u\ \text{and }v")
                swap_text.set_color(WHITE)
                swap_text.scale(0.74)
                swap_text.next_to(update_text, DOWN, aligned_edge=LEFT, buff=0.18)
                self.play(Write(swap_text), run_time=0.7)

                u, v = v.copy(), u.copy()
                new_basis = build_basis_group(u, v)
                new_cell = build_cell_group(u, v)
                new_status = pin_status_block(build_status_block(u, v))

                self.play(
                    ReplacementTransform(basis_group, new_basis),
                    ReplacementTransform(cell_group, new_cell),
                    ReplacementTransform(status_block, new_status),
                    run_time=1.0,
                )
                self.wait(1.0)
                basis_group = new_basis
                cell_group = new_cell
                status_block = new_status
                self.play(FadeOut(swap_text), run_time=0.4)

            self.play(FadeOut(compute_text), FadeOut(update_text), run_time=0.4)

            history_rows.append(pending_row)
            new_history_table = pin_history_table(build_history_table(history_rows))
            self.play(ReplacementTransform(history_table, new_history_table), run_time=0.8)
            history_table = new_history_table
            self.wait(1.0)

        final_box = SurroundingRectangle(status_block, color=GREEN, buff=0.12)
        final_text = Text("Returned reduced basis [u, v]", font_size=30, color=GREEN)
        final_text.next_to(final_box, DOWN, buff=0.25)

        self.play(ShowCreation(final_box), Write(final_text), run_time=1.0)
        self.wait(2.0)