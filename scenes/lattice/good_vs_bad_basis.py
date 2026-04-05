from manimlib import *


class GoodVsBadBasis(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        final_frame_width = 56.0
        self.camera.frame.set_width(10.0)

        # Same grid styling as previous scenes.
        plane = NumberPlane(
            x_range=(-80, 80, 1),
            y_range=(-60, 60, 1),
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
        self.add(plane)

        bad_color = "#8DF5B2"   # light green
        good_color = "#F48CFF"  # light magenta

        # Matrices from prompt (columns used as basis vectors).
        # B' = [[19, 21], [-1, -1]]  => b1'=(19,-1), b2'=(21,-1)
        # B  = [[1,  1],  [-1, 1]]   => b1=(1,-1),  b2=(1,1)
        # Literal view: no display scaling and no translated duplicate anchors.
        anchor = (0.0, 0.0)
        bad_b1 = (19.0, -1.0)
        bad_b2 = (21.0, -1.0)
        good_b1 = (1.0, -1.0)
        good_b2 = (1.0, 1.0)

        def c2p(x, y):
            return plane.c2p(x, y)

        def basis_vectors(anchor, b1, b2, color):
            p0 = c2p(anchor[0], anchor[1])
            p1 = c2p(anchor[0] + b1[0], anchor[1] + b1[1])
            p2 = c2p(anchor[0] + b2[0], anchor[1] + b2[1])

            v1 = Arrow(p0, p1, buff=0)
            v1.set_color(color)
            v1.set_stroke(color=color, width=4, opacity=1.0)

            v2 = Arrow(p0, p2, buff=0)
            v2.set_color(color)
            v2.set_stroke(color=color, width=4, opacity=1.0)

            return VGroup(v1, v2)

        def fundamental_cell(anchor, b1, b2, color):
            p0 = c2p(anchor[0], anchor[1])
            p1 = c2p(anchor[0] + b1[0], anchor[1] + b1[1])
            p2 = c2p(anchor[0] + b1[0] + b2[0], anchor[1] + b1[1] + b2[1])
            p3 = c2p(anchor[0] + b2[0], anchor[1] + b2[1])

            fill = Polygon(p0, p1, p2, p3, stroke_width=0)
            fill.set_fill(color, opacity=0.14)

            edges = VGroup(
                DashedLine(p0, p1, color=color, stroke_width=2.6),
                DashedLine(p1, p2, color=color, stroke_width=2.6),
                DashedLine(p2, p3, color=color, stroke_width=2.6),
                DashedLine(p3, p0, color=color, stroke_width=2.6),
            )
            return VGroup(fill, edges)

        bad_vectors = basis_vectors(anchor, bad_b1, bad_b2, bad_color)
        bad_cell = fundamental_cell(anchor, bad_b1, bad_b2, bad_color)

        good_vectors = basis_vectors(anchor, good_b1, good_b2, good_color)
        good_cell = fundamental_cell(anchor, good_b1, good_b2, good_color)

        # Start zoomed in on where B is drawn.
        self.camera.frame.move_to(c2p(0.0, 0.0))

        full_view_center = c2p(20.0, 0.0)

        # 1) Draw B basis vectors first.
        self.play(ShowCreation(good_vectors[0]), ShowCreation(good_vectors[1]), run_time=1.2)

        # 2) Draw B dashed fundamental cell + same-color overlay.
        self.play(FadeIn(good_cell[0]), ShowCreation(good_cell[1]), run_time=1.3)

        # 3) Draw B' while gradually zooming out.
        self.play(
            ShowCreation(bad_vectors[0]),
            ShowCreation(bad_vectors[1]),
            self.camera.frame.animate.move_to(c2p(12.0, 0.0)).set_width(32.0),
            run_time=2.2,
        )

        # 4) Continue drawing B' cell and complete zoom-out to full view.
        self.play(
            FadeIn(bad_cell[0]),
            ShowCreation(bad_cell[1]),
            self.camera.frame.animate.move_to(full_view_center).set_width(final_frame_width),
            run_time=2.4,
        )
        self.wait(1.0)
