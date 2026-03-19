from manimlib import *
import numpy as np

class GaussLatticeReduction(Scene):
    def construct(self):
        # Configuration
        v1_coords = np.array([3.0, 1.0, 0.0])
        v2_coords = np.array([4.0, 3.0, 0.0])
        
        c1 = TEAL
        c2 = MAROON
        lattice_color = GREY
        lattice_opacity = 0.5
        
        # Header
        title = Text("Gauss's Lattice Reduction Algorithm", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))
        
        # --- Setup Initial State ---
        v1 = Vector(v1_coords, color=c1)
        v2 = Vector(v2_coords, color=c2)
        
        label1 = Tex("v_1").next_to(v1.get_end(), RIGHT + DOWN, buff=0.1).set_color(c1)
        label2 = Tex("v_2").next_to(v2.get_end(), UP + LEFT, buff=0.1).set_color(c2)
        
        def get_lattice_dots(b1, b2, x_range=(-6, 7), y_range=(-6, 7)):
            dots = VGroup()
            for x in range(x_range[0], x_range[1]):
                for y in range(y_range[0], y_range[1]):
                    point = x * b1 + y * b2
                    dot = Dot(point, radius=0.05, color=lattice_color, fill_opacity=lattice_opacity)
                    dots.add(dot)
            return dots

        current_v1_array = v1_coords.copy()
        current_v2_array = v2_coords.copy()

        lattice_dots = get_lattice_dots(current_v1_array, current_v2_array)
        
        self.play(
            ShowCreation(v1), Write(label1),
            ShowCreation(v2), Write(label2)
        )
        self.play(ShowCreation(lattice_dots), run_time=2)
        self.wait(1)

        def get_basis_text(v1_arr, v2_arr):
            return VGroup(
                Tex(f"v_1 = [{int(round(v1_arr[0]))}, {int(round(v1_arr[1]))}]", color=c1),
                Tex(f"v_2 = [{int(round(v2_arr[0]))}, {int(round(v2_arr[1]))}]", color=c2)
            ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL).shift(DOWN * 0.5)

        info_text = get_basis_text(current_v1_array, current_v2_array)
        self.play(Write(info_text))
        
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
                
                new_v1 = Vector(current_v1_array, color=c1)
                new_v2 = Vector(current_v2_array, color=c2)
                
                new_label1 = Tex("v_1").next_to(new_v1.get_end(), RIGHT + DOWN, buff=0.1).set_color(c1)
                new_label2 = Tex("v_2").next_to(new_v2.get_end(), UP + LEFT, buff=0.1).set_color(c2)
                new_info_text = get_basis_text(current_v1_array, current_v2_array).move_to(info_text.get_center())

                self.play(
                    ReplacementTransform(v1, new_v1),
                    ReplacementTransform(v2, new_v2),
                    ReplacementTransform(label1, new_label1),
                    ReplacementTransform(label2, new_label2),
                    ReplacementTransform(info_text, new_info_text),
                )
                self.play(FadeOut(swap_text))
                
                # References updated cleanly
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
                final_text = Text("Algorithm Terminated (m=0)", color=GREEN, font_size=24).next_to(calc_text, DOWN, aligned_edge=LEFT)
                self.play(Write(final_text))
                self.wait(2)
                break
            
            # Visualizing the Projection Intuition
            span_line = Line(current_v1_array * -10, current_v1_array * 10, color=c1, stroke_opacity=0.3)
            exact_proj_point = (dot_prod / norm_sq) * current_v1_array
            perp_line = DashedLine(current_v2_array, exact_proj_point, color=WHITE, stroke_opacity=0.6)
            
            m_v1_point = m * current_v1_array
            m_dot = Dot(m_v1_point, color=YELLOW)
            
            self.play(ShowCreation(span_line))
            self.play(ShowCreation(perp_line))
            self.play(ShowCreation(m_dot))
            self.wait(1)

            # Step 3: Reduction
            action_text = Tex(f"v_2 \\leftarrow v_2 - {m}v_1", color=RED).next_to(calc_text, DOWN, aligned_edge=LEFT)
            self.play(Write(action_text))
            
            shift_vec = -m * current_v1_array
            sub_arrow = Arrow(current_v2_array, current_v2_array + shift_vec, color=RED, buff=0)
            self.play(ShowCreation(sub_arrow))
            self.wait(0.5)
            
            next_v2_array = current_v2_array + shift_vec
            new_v2 = Vector(next_v2_array, color=c2)
            new_label2 = Tex("v_2").next_to(new_v2.get_end(), UP+LEFT, buff=0.1).set_color(c2)
            new_info_text = get_basis_text(current_v1_array, next_v2_array).move_to(info_text.get_center())

            # FIX APPLIED HERE: ReplacementTransform for info_text
            self.play(
                ReplacementTransform(v2, new_v2),
                ReplacementTransform(label2, new_label2),
                ReplacementTransform(info_text, new_info_text), 
                FadeOut(sub_arrow), FadeOut(perp_line), 
                FadeOut(span_line), FadeOut(m_dot)
            )
            
            # FIX APPLIED HERE: Updating the info_text reference for the next loop
            v2 = new_v2
            label2 = new_label2
            info_text = new_info_text 
            current_v2_array = next_v2_array
            
            self.play(FadeOut(calc_text), FadeOut(action_text))
            self.wait(0.5)

        # Highlight final basis
        rect = SurroundingRectangle(info_text, color=GREEN)
        self.play(ShowCreation(rect))
        
        ortho_text = Text("Reduced Orthogonal Basis", font_size=36, color=GREEN).next_to(rect, RIGHT)
        self.play(Write(ortho_text))
        
        self.play(Flash(lattice_dots, color=WHITE, run_time=2))
        self.wait(3)