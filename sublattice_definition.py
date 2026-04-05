from manimlib import *


class SublatticeDefinition(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        self.camera.frame.set_width(14.5)

        color_L3 = TEAL
        color_L1 = MAROON
        color_overlap = interpolate_color(color_L3, color_L1, 0.5)

        plane = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
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
        l3_b1 = plane.c2p(2, 0) - origin
        l3_b2 = plane.c2p(0, 1) - origin
        l1_b1 = plane.c2p(1, 0) - origin
        l1_b2 = plane.c2p(0, 1) - origin

        def make_cell(b1_shift, b2_shift, color):
            p0 = origin
            p1 = origin + b1_shift
            p2 = origin + b1_shift + b2_shift
            p3 = origin + b2_shift

            fill = Polygon(p0, p1, p2, p3, stroke_width=0)
            fill.set_fill(color, opacity=0.14)
            edges = VGroup(
                DashedLine(p0, p1, color=color, stroke_width=2.5),
                DashedLine(p1, p2, color=color, stroke_width=2.5),
                DashedLine(p2, p3, color=color, stroke_width=2.5),
                DashedLine(p3, p0, color=color, stroke_width=2.5),
            )
            return fill, edges

        l3_fill, l3_edges = make_cell(l3_b1, l3_b2, color_L3)
        l1_fill, l1_edges = make_cell(l1_b1, l1_b2, color_L1)

        # Start with grid + L3 fundamental parallelepiped pre-drawn.
        self.add(plane, l3_fill, l3_edges)

        # Overlay L1 fundamental parallelepiped in a distinct color.
        self.play(FadeIn(l1_fill), ShowCreation(l1_edges), run_time=1.1)

        x_vals = list(range(-8, 9))
        y_vals = list(range(-5, 6))

        l1_points = {(x, y) for x in x_vals for y in y_vals}
        l3_points = {(x, y) for x in x_vals for y in y_vals if x % 2 == 0}
        overlap_points = l1_points & l3_points
        l1_only_points = l1_points - overlap_points

        l3_dots = VGroup()
        l3_dot_map = {}
        for x, y in sorted(l3_points, key=lambda p: (p[0] * p[0] + p[1] * p[1], abs(p[1]), abs(p[0]))):
            dot = Dot(plane.c2p(x, y), radius=0.05, color=color_L3)
            dot.set_fill(color_L3, opacity=1.0)
            dot.set_stroke(color_L3, width=0, opacity=1.0)
            l3_dots.add(dot)
            l3_dot_map[(x, y)] = dot

        l1_only_dots = VGroup()
        for x, y in sorted(l1_only_points, key=lambda p: (p[0] * p[0] + p[1] * p[1], abs(p[1]), abs(p[0]))):
            dot = Dot(plane.c2p(x, y), radius=0.05, color=color_L1)
            dot.set_fill(color_L1, opacity=1.0)
            dot.set_stroke(color_L1, width=0, opacity=1.0)
            l1_only_dots.add(dot)

        # L3 lattice points.
        self.play(FadeIn(l3_dots, lag_ratio=0.01), run_time=2.2)

        # L1 lattice points; then recolor overlap to the mixed color.
        self.play(FadeIn(l1_only_dots, lag_ratio=0.01), run_time=2.0)

        overlap_recolor_anims = []
        for point in sorted(overlap_points, key=lambda p: (p[0] * p[0] + p[1] * p[1], abs(p[1]), abs(p[0]))):
            dot = l3_dot_map[point]
            overlap_recolor_anims.append(
                dot.animate.set_fill(color_overlap, opacity=1.0).set_stroke(color_overlap, width=0, opacity=1.0)
            )
        if overlap_recolor_anims:
            self.play(LaggedStart(*overlap_recolor_anims, lag_ratio=0.01), run_time=1.4)

        def make_tiling_groups(b1_shift, b2_shift, color, i_range, j_range):
            indices = []
            for i in i_range:
                for j in j_range:
                    if (i, j) == (0, 0):
                        continue
                    indices.append((i, j))

            indices.sort(key=lambda ij: (ij[0] ** 2 + ij[1] ** 2, abs(ij[1]), abs(ij[0])))

            tile_groups = []
            for i, j in indices:
                shift_vec = i * b1_shift + j * b2_shift

                p0 = origin + shift_vec
                p1 = p0 + b1_shift
                p2 = p1 + b2_shift
                p3 = p0 + b2_shift

                tile_fill = Polygon(p0, p1, p2, p3, stroke_width=0)
                tile_fill.set_fill(color, opacity=0.0)

                e1 = DashedLine(p0, p1, color=color, stroke_width=2.0)
                e2 = DashedLine(p1, p2, color=color, stroke_width=2.0)
                e3 = DashedLine(p2, p3, color=color, stroke_width=2.0)
                e4 = DashedLine(p3, p0, color=color, stroke_width=2.0)
                e1.set_stroke(opacity=0.0)
                e2.set_stroke(opacity=0.0)
                e3.set_stroke(opacity=0.0)
                e4.set_stroke(opacity=0.0)

                tile_groups.append(VGroup(tile_fill, e1, e2, e3, e4))

            return tile_groups

        # Span the grid with L3 first (same nearest-first lag style as previous scenes).
        l3_tiles = make_tiling_groups(l3_b1, l3_b2, color_L3, range(-5, 6), range(-6, 7))
        if l3_tiles:
            self.add(*l3_tiles)
            self.play(
                LaggedStart(
                    *[
                        AnimationGroup(
                            tile[0].animate.set_fill(opacity=0.12),
                            tile[1].animate.set_stroke(opacity=1.0),
                            tile[2].animate.set_stroke(opacity=1.0),
                            tile[3].animate.set_stroke(opacity=1.0),
                            tile[4].animate.set_stroke(opacity=1.0),
                        )
                        for tile in l3_tiles
                    ],
                    lag_ratio=0.03,
                ),
                run_time=5.6,
            )

        # Then span the grid with L1 using the same animation style.
        l1_tiles = make_tiling_groups(l1_b1, l1_b2, color_L1, range(-8, 9), range(-6, 7))
        if l1_tiles:
            self.add(*l1_tiles)
            self.play(
                LaggedStart(
                    *[
                        AnimationGroup(
                            tile[0].animate.set_fill(opacity=0.07),
                            tile[1].animate.set_stroke(opacity=1.0),
                            tile[2].animate.set_stroke(opacity=1.0),
                            tile[3].animate.set_stroke(opacity=1.0),
                            tile[4].animate.set_stroke(opacity=1.0),
                        )
                        for tile in l1_tiles
                    ],
                    lag_ratio=0.025,
                ),
                run_time=5.6,
            )

        self.wait(1.5)
