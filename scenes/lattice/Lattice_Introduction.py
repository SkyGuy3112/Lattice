from manimlib import *

class LatticeIntroduction(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # 1) Frame centered at origin with a visible 2D grid
        plane = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1.2,
                "stroke_opacity": 0.3,   # gray + transparent
            },
            axis_config={
                "stroke_color": GREY,
                "stroke_width": 2,
                "stroke_opacity": 0.5,
            },
        )

        self.play(ShowCreation(plane), run_time=1.8)
        self.wait(0.3)

        # 2) Basis vectors for B1 = [(1,0), (0,1)]
        origin = plane.c2p(0, 0)
        b1_end = plane.c2p(1, 0)   # horizontal basis vector
        b2_end = plane.c2p(0, 1)   # vertical basis vector

        # Basis colors requested
        b1_color = MAROON
        b2_color = TEAL

        b1_vec = Arrow(origin, b1_end, buff=0)
        b1_vec.set_color(b1_color)
        b1_vec.set_stroke(color=b1_color, opacity=1.0)

        b2_vec = Arrow(origin, b2_end, buff=0)
        b2_vec.set_color(b2_color)
        b2_vec.set_stroke(color=b2_color, opacity=1.0)

        # Ordered-pair labels (white), positioned as requested
        b1_label = Tex("(1,0)").set_color(WHITE).next_to(b1_end, DOWN, buff=0.12)
        b2_label = Tex("(0,1)").set_color(WHITE).next_to(b2_end, LEFT + UP, buff=0.12)

        self.play(
            ShowCreation(b1_vec),
            ShowCreation(b2_vec),
            Write(b1_label),
            Write(b2_label),
            run_time=1.6,
        )
        self.wait(0.4)

        # 3) Lattice points covering the whole visible frame
        lattice_points = VGroup()
        for i in range(-8, 9):
            for j in range(-5, 6):
                lattice_points.add(
                    Dot(
                        plane.c2p(i, j),
                        radius=0.045,
                        fill_color=YELLOW,
                        fill_opacity=0.9,
                        stroke_color=YELLOW,
                        stroke_opacity=0.9,
                        stroke_width=0,
                    )
                )

        self.play(FadeIn(lattice_points, lag_ratio=0.01), run_time=2.0)

        # 4) Visual cue that the lattice span engulfs the whole frame
        span_overlay = FullScreenRectangle(fill_color=YELLOW, fill_opacity=0.0, stroke_width=0)
        span_overlay.set_fill(YELLOW, opacity=0.0)

        self.add(span_overlay)
        self.play(
            span_overlay.animate.set_fill(opacity=0.08),
            run_time=1.8,
        )
        self.play(span_overlay.animate.set_fill(opacity=0.0), run_time=0.9)
        self.wait(1.5)