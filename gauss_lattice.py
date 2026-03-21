from manimlib import *
import numpy as np

class GaussLatticeReduction(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        self.camera.background_rgba = np.array([0.0, 0.0, 0.0, 1.0])

        # Hard backdrop to avoid renderer/theme gray backgrounds.
        backdrop = FullScreenRectangle(fill_color=BLACK, fill_opacity=1, stroke_width=0)
        backdrop.set_z_index(-100)
        self.add(backdrop)

        # Cartesian reference frame for easier geometric reading.
        plane = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1,
                "stroke_opacity": 0.2,
            },
        )
        axes = Axes(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
            axis_config={
                "color": GREY,
                "stroke_width": 2,
                "stroke_opacity": 0.6,
            },
        )
        x_label = Tex("x").set_color(GREY).next_to(axes.x_axis.get_end(), RIGHT, buff=0.12)
        y_label = Tex("y").set_color(GREY).next_to(axes.y_axis.get_end(), UP, buff=0.12)
        self.add(plane, axes, x_label, y_label)

        origin_point = axes.c2p(0, 0)

        def to_cart_point(arr):
            return axes.c2p(arr[0], arr[1])

        def basis_arrow(arr, color=WHITE):
            return Arrow(origin_point, to_cart_point(arr), buff=0, color=color)

        # Configuration
        v1_coords = np.array([3.0, 1.0, 0.0])
        v2_coords = np.array([4.0, 3.0, 0.0])
        
        # --- VISUAL FIXES APPLIED HERE ---
        c1 = TEAL
        c2 = MAROON
        lattice_color = YELLOW  # Changed from GREY to YELLOW
        lattice_opacity = 0.6   # Bumped opacity slightly so the yellow pops
        
        # Header (commented out to save screen space)
        # title = Text("Gauss's Lattice Reduction Algorithm", font_size=40)
        # title.to_edge(UP)
        # self.play(Write(title))
        
        # --- Setup Initial State ---
        v1 = basis_arrow(v1_coords, color=WHITE)
        v2 = basis_arrow(v2_coords, color=WHITE)
        
        label1 = Tex("v_1").set_color(c1).next_to(v1.get_end(), RIGHT + DOWN, buff=0.1)
        label2 = Tex("v_2").set_color(c2).next_to(v2.get_end(), UP + LEFT, buff=0.1)
        
        # def get_lattice_dots(b1, b2, x_range=(-6, 7), y_range=(-6, 7)):
        #     dots = VGroup()
        #     for x in range(x_range[0], x_range[1]):
        #         for y in range(y_range[0], y_range[1]):
        #             point = x * b1 + y * b2
        #             dot = Dot(
        #                 to_cart_point(point),
        #                 radius=0.05,
        #                 fill_color=lattice_color,
        #                 fill_opacity=lattice_opacity,
        #                 stroke_color=lattice_color,
        #                 stroke_opacity=lattice_opacity,
        #                 stroke_width=0,
        #             )
        #             dots.add(dot)
        #     return dots

        current_v1_array = v1_coords.copy()
        current_v2_array = v2_coords.copy()

        # lattice_dots = get_lattice_dots(current_v1_array, current_v2_array)
        
        self.play(
            ShowCreation(v1), Write(label1),
            ShowCreation(v2), Write(label2)
        )
        # self.play(ShowCreation(lattice_dots), run_time=2)
        self.wait(1)

        def get_basis_text(v1_arr, v2_arr):
            line1 = Tex(f"v_1 = ({int(round(v1_arr[0]))}, {int(round(v1_arr[1]))})").set_color(c1)
            line2 = Tex(f"v_2 = ({int(round(v2_arr[0]))}, {int(round(v2_arr[1]))})").set_color(c2)
            return VGroup(line1, line2).arrange(DOWN, aligned_edge=LEFT).to_corner(UL).shift(DOWN * 0.5)

        def get_fundamental_cell(b1, b2, color, fill_opacity=0.2):
            return Polygon(
                origin_point,
                to_cart_point(b1),
                to_cart_point(b1 + b2),
                to_cart_point(b2),
                color=color,
                fill_color=color,
                fill_opacity=fill_opacity,
                stroke_width=2,
            )

        def get_cell_edge_vectors(b1, b2):
            edge1 = Arrow(origin_point, to_cart_point(b1), buff=0, color=c1, stroke_width=4)
            edge2 = Arrow(origin_point, to_cart_point(b2), buff=0, color=c2, stroke_width=4)
            edge1_label = Tex("v_1").set_color(c1).next_to(edge1.get_end(), RIGHT + DOWN, buff=0.08)
            edge2_label = Tex("v_2").set_color(c2).next_to(edge2.get_end(), UP + LEFT, buff=0.08)
            return VGroup(edge1, edge2, edge1_label, edge2_label)

        info_text = get_basis_text(current_v1_array, current_v2_array)
        self.play(Write(info_text))

        # Intro: Fundamental cell before reduction.
        before_cell = get_fundamental_cell(current_v1_array, current_v2_array, BLUE, fill_opacity=0.22)
        before_edges = get_cell_edge_vectors(current_v1_array, current_v2_array)
        before_cell_text = Text(
            "Fundamental cell (before reduction)",
            font_size=24,
            color=BLUE,
        ).to_edge(DOWN)
        self.play(
            ShowCreation(before_cell),
            ShowCreation(before_edges[0]),
            ShowCreation(before_edges[1]),
            Write(before_edges[2]),
            Write(before_edges[3]),
            FadeIn(before_cell_text, UP),
        )
        self.wait(1)
        self.play(FadeOut(before_cell), FadeOut(before_edges), FadeOut(before_cell_text))
        
        # --- Algorithm Loop ---
        step_count = 0
        while step_count < 10:
            step_count += 1
            
            # Step 1: Ensure |v1| <= |v2|
            norm1 = np.linalg.norm(current_v1_array)
            norm2 = np.linalg.norm(current_v2_array)
            
            if norm2 < norm1:
                self.play(Flash(info_text, color=YELLOW), run_time=0.5)
                
                swap_text = Text("Swap basis vectors", font_size=24, color=YELLOW).next_to(info_text, DOWN)
                self.play(FadeIn(swap_text, UP))
                
                current_v1_array, current_v2_array = current_v2_array, current_v1_array
                
                new_v1 = basis_arrow(current_v1_array, color=WHITE)
                new_v2 = basis_arrow(current_v2_array, color=WHITE)
                
                new_label1 = Tex("v_1").set_color(c1).next_to(new_v1.get_end(), RIGHT + DOWN, buff=0.1)
                new_label2 = Tex("v_2").set_color(c2).next_to(new_v2.get_end(), UP + LEFT, buff=0.1)
                new_info_text = get_basis_text(current_v1_array, current_v2_array).move_to(info_text.get_center())

                self.play(
                    ReplacementTransform(v1, new_v1),
                    ReplacementTransform(v2, new_v2),
                    ReplacementTransform(label1, new_label1),
                    ReplacementTransform(label2, new_label2),
                    ReplacementTransform(info_text, new_info_text),
                )
                self.play(FadeOut(swap_text))
                
                v1, v2 = new_v1, new_v2
                label1, label2 = new_label1, new_label2
                info_text = new_info_text
                self.wait(0.5)
            
            # Step 2: Calculate Projection coefficient m
            dot_prod = np.dot(current_v1_array, current_v2_array)
            norm_sq = np.dot(current_v1_array, current_v1_array)
            m = int(round(dot_prod / norm_sq))
            
            calc_text = Tex(f"m = \\lfloor \\frac{{v_1 \\cdot v_2}}{{|v_1|^2}} \\rceil = {m}", font_size=30)
            calc_text.next_to(info_text, DOWN, aligned_edge=LEFT)
            self.play(Write(calc_text))
            self.wait(0.5)

            if m == 0:
                final_text = Text(
                    "Algorithm Terminated (m=0)",
                    color=GREEN,
                    font_size=24,
                    font="Times New Roman",
                ).next_to(calc_text, DOWN, aligned_edge=LEFT)
                self.play(Write(final_text))
                self.wait(2)
                break
            
            # Visualizing the Projection Intuition
            span_line = Line(
                to_cart_point(current_v1_array * -10),
                to_cart_point(current_v1_array * 10),
                color=c1,
                stroke_opacity=0.3,
            )
            exact_proj_point = (dot_prod / norm_sq) * current_v1_array
            perp_line = DashedLine(
                to_cart_point(current_v2_array),
                to_cart_point(exact_proj_point),
                color=WHITE,
                stroke_opacity=0.6,
            )
            proj_dot = Dot(to_cart_point(exact_proj_point), color=WHITE, radius=0.06)
            proj_label = Tex(r"\mathrm{proj}_{v_1}(v_2)", color=WHITE, font_size=26).next_to(
                proj_dot,
                UP + RIGHT,
                buff=0.1,
            )
            
            m_v1_point = m * current_v1_array
            m_dot = Dot(to_cart_point(m_v1_point), color=YELLOW)
            
            self.play(ShowCreation(span_line))
            self.play(ShowCreation(perp_line))
            self.play(FadeIn(proj_dot), Write(proj_label))
            self.play(ShowCreation(m_dot))
            self.wait(1)

            # Step 3: Reduction
            action_text = Tex(f"v_2 \\leftarrow v_2 - {m}v_1", color=RED).next_to(calc_text, DOWN, aligned_edge=LEFT)
            self.play(Write(action_text))
            
            shift_vec = -m * current_v1_array
            sub_arrow = Arrow(
                to_cart_point(current_v2_array),
                to_cart_point(current_v2_array + shift_vec),
                color=RED,
                buff=0,
            )
            self.play(ShowCreation(sub_arrow))
            self.wait(0.5)
            
            next_v2_array = current_v2_array + shift_vec
            new_v2 = basis_arrow(next_v2_array, color=WHITE)
            
            new_label2 = Tex("v_2").set_color(c2).next_to(new_v2.get_end(), UP+LEFT, buff=0.1)
            new_info_text = get_basis_text(current_v1_array, next_v2_array).move_to(info_text.get_center())

            self.play(
                ReplacementTransform(v2, new_v2),
                ReplacementTransform(label2, new_label2),
                ReplacementTransform(info_text, new_info_text), 
                FadeOut(sub_arrow), FadeOut(perp_line), 
                FadeOut(span_line), FadeOut(m_dot),
                FadeOut(proj_dot), FadeOut(proj_label)
            )
            
            v2 = new_v2
            label2 = new_label2
            info_text = new_info_text 
            current_v2_array = next_v2_array
            
            self.play(FadeOut(calc_text), FadeOut(action_text))
            self.wait(0.5)

        # Fundamental cell after reduction.
        after_cell = get_fundamental_cell(current_v1_array, current_v2_array, GREEN, fill_opacity=0.26)
        after_edges = get_cell_edge_vectors(current_v1_array, current_v2_array)
        after_cell_text = Text(
            "Fundamental cell (after reduction)",
            font_size=24,
            color=GREEN,
        ).to_edge(DOWN)
        self.play(
            ShowCreation(after_cell),
            ShowCreation(after_edges[0]),
            ShowCreation(after_edges[1]),
            Write(after_edges[2]),
            Write(after_edges[3]),
            FadeIn(after_cell_text, UP),
        )
        self.wait(1)
        self.play(FadeOut(after_cell), FadeOut(after_edges), FadeOut(after_cell_text))

        # Highlight final basis
        rect = SurroundingRectangle(info_text, color=GREEN)
        self.play(ShowCreation(rect))
        
        ortho_text = Text(
            "Reduced Basis",
            font_size=36,
            color=GREEN,
            font="Times New Roman",
        ).next_to(rect, RIGHT)
        self.play(Write(ortho_text))
        
        # self.play(Flash(lattice_dots, color=WHITE, run_time=2))
        self.wait(3)