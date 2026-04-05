from manimlib import *
import numpy as np


class UniqueRepresentationB2(Scene):
	def construct(self):
		self.camera.background_color = BLACK
		self.camera.frame.set_width(18.0)

		# 1) Pre-drawn grid with ordered basis B2 = {(2,0), (1,1)}.
		plane = NumberPlane(
			x_range=(-10, 10, 1),
			y_range=(-6, 6, 1),
			background_line_style={
				"stroke_color": GREY,
				"stroke_width": 1.2,
				"stroke_opacity": 0.3,
			},
			axis_config={
				"stroke_color": GREY,
				"stroke_width": 2,
				"stroke_opacity": 0.5,
			},
		)

		origin = plane.c2p(0, 0)
		b1_vec_xy = np.array([2.0, 0.0, 0.0])
		b2_vec_xy = np.array([1.0, 1.0, 0.0])
		b1_end = plane.c2p(2, 0)
		b2_end = plane.c2p(1, 1)

		b1_vec = Arrow(origin, b1_end, buff=0)
		b1_vec.set_color(MAROON)
		b1_vec.set_stroke(color=MAROON, opacity=1.0)

		b2_vec = Arrow(origin, b2_end, buff=0)
		b2_vec.set_color(TEAL)
		b2_vec.set_stroke(color=TEAL, opacity=1.0)

		self.add(plane, b1_vec, b2_vec)

		# 2) Add a point v and its ordered pair.
		v_xy = np.array([4.2, 1.35, 0.0])
		v_point = Dot(plane.c2p(v_xy[0], v_xy[1]), radius=0.06, color=PURPLE)
		v_point.set_fill(PURPLE, opacity=1.0)
		v_label = Tex("v(4.2,\,1.35)")
		v_label.set_color(PURPLE)
		v_label.scale(0.75)
		v_label.next_to(v_point, UP + RIGHT, buff=0.12)
		self.play(FadeIn(v_point), Write(v_label), run_time=1.0)

		# 3) Draw fundamental cell and tile space with circular fade ordering.
		top_right = plane.c2p(3, 1)
		edge_from_b1 = DashedLine(b1_end, top_right, color=YELLOW, stroke_width=3)
		edge_from_b2 = DashedLine(b2_end, top_right, color=YELLOW, stroke_width=3)
		cell_fill = Polygon(origin, b1_end, top_right, b2_end, stroke_width=0)
		cell_fill.set_fill(YELLOW, opacity=0.12)

		fundamental_cell = VGroup(cell_fill, edge_from_b1, edge_from_b2)
		self.play(
			ShowCreation(edge_from_b1),
			ShowCreation(edge_from_b2),
			FadeIn(cell_fill),
			run_time=1.3,
		)

		# Find containing tile index for v under half-open coefficients in B2 basis.
		a2 = v_xy[1]
		a1 = 0.5 * (v_xy[0] - v_xy[1])
		i0 = int(np.floor(a1))
		j0 = int(np.floor(a2))

		shift_b1 = plane.c2p(2, 0) - origin
		shift_b2 = plane.c2p(1, 1) - origin

		x_min, x_max = -10, 10
		y_min, y_max = -6, 6
		base_center = np.array([1.5, 0.5, 0.0])

		candidate_indices = []
		for i in range(-9, 10):
			for j in range(-8, 9):
				if (i, j) == (0, 0):
					continue

				center = base_center + i * b1_vec_xy + j * b2_vec_xy
				if x_min - 2 <= center[0] <= x_max + 2 and y_min - 1 <= center[1] <= y_max + 1:
					candidate_indices.append((i, j))

		candidate_indices.sort(key=lambda ij: (ij[0] ** 2 + ij[1] ** 2, abs(ij[1]), abs(ij[0])))

		tile_groups = []
		containing_tile = None
		for i, j in candidate_indices:
			shift_vec = i * shift_b1 + j * shift_b2

			tile_fill = cell_fill.copy()
			tile_fill.shift(shift_vec)
			tile_fill.set_fill(YELLOW, opacity=0.0)

			tile_edge_b1 = edge_from_b1.copy()
			tile_edge_b1.shift(shift_vec)
			tile_edge_b1.set_stroke(YELLOW, width=3, opacity=0.0)

			tile_edge_b2 = edge_from_b2.copy()
			tile_edge_b2.shift(shift_vec)
			tile_edge_b2.set_stroke(YELLOW, width=3, opacity=0.0)

			tile_group = VGroup(tile_fill, tile_edge_b1, tile_edge_b2)
			tile_groups.append(tile_group)
			if (i, j) == (i0, j0):
				containing_tile = tile_group

		if tile_groups:
			self.add(*tile_groups)
			self.play(
				LaggedStart(
					*[
						AnimationGroup(
							tile_group[0].animate.set_fill(opacity=0.12),
							tile_group[1].animate.set_stroke(opacity=1.0),
							tile_group[2].animate.set_stroke(opacity=1.0),
						)
						for tile_group in tile_groups
					],
					lag_ratio=0.03,
				),
				run_time=6.0,
			)

		# 4) Keep only the tile containing v, then zoom to focus on it.
		if containing_tile is None:
			containing_anchor = plane.c2p(2 * i0 + j0, j0)
			containing_tile = fundamental_cell.copy().shift(containing_anchor - origin)
			self.add(containing_tile)

		fade_targets = [fundamental_cell]
		fade_targets.extend([tg for tg in tile_groups if tg is not containing_tile])
		if fade_targets:
			self.play(*[FadeOut(mob) for mob in fade_targets], run_time=1.2)

		self.play(
			self.camera.frame.animate.move_to(containing_tile.get_center()).set_width(7.0),
			run_time=1.6,
		)

		# 5) Show color-coded unique decomposition on the top-left of the frame.
		decomp = Tex("v", "=", "L", "+", "f")
		decomp.set_color(WHITE)
		decomp[0].set_color(PURPLE)
		decomp[2].set_color(BLUE)
		decomp[4].set_color(RED)
		decomp.scale(0.9)
		decomp.move_to(self.camera.frame.get_corner(UL) + RIGHT * 1.6 + DOWN * 0.7)
		self.play(Write(decomp), run_time=1.0)

		# 6) Add lattice definition under the decomposition (for anchor vx).
		lattice_def = Tex(r"v_x\in L_2=L(B_2)=\{B_2x:\,x\in\mathbb{Z}^2\}")
		lattice_def.set_color(BLUE)
		lattice_def.scale(0.58)
		lattice_def.next_to(decomp, DOWN, aligned_edge=LEFT, buff=0.2)
		self.play(Write(lattice_def), run_time=1.2)


		# 7) Anchor-point naming and anchor mapping.
		anchor_xy = np.array([2 * i0 + j0, j0, 0.0])
		anchor_point = Dot(plane.c2p(anchor_xy[0], anchor_xy[1]), radius=0.05, color=BLUE)
		anchor_point.set_fill(BLUE, opacity=1.0)
		anchor_label = Tex(r"v_x")
		anchor_label.set_color(BLUE)
		anchor_label.scale(0.72)
		anchor_label.next_to(anchor_point, DOWN + LEFT, buff=0.12)
		anchor_pair_tex = f"({int(anchor_xy[0])},{int(anchor_xy[1])})"
		anchor_pair = Tex(anchor_pair_tex)
		anchor_pair.set_color(BLUE)
		anchor_pair.scale(0.55)
		anchor_pair.next_to(anchor_label, DOWN, aligned_edge=LEFT, buff=0.05)

		anchor_line = DashedLine(
			plane.c2p(v_xy[0], v_xy[1]),
			plane.c2p(anchor_xy[0], anchor_xy[1]),
			color=BLUE,
			stroke_width=2.5,
		)
		self.play(
			FadeIn(anchor_point),
			Write(anchor_label),
			Write(anchor_pair),
			ShowCreation(anchor_line),
			run_time=1.2,
		)

		# 8) Red component guides from v to anchor-aligned tile edges.
		proj_vertical_xy = np.array([v_xy[0], anchor_xy[1], 0.0])
		# Horizontal guide should extend to the anchor x-gridline.
		proj_horizontal_xy = np.array([anchor_xy[0], v_xy[1], 0.0])

		f_vertical_line = DashedLine(
			plane.c2p(v_xy[0], v_xy[1]),
			plane.c2p(proj_vertical_xy[0], proj_vertical_xy[1]),
			color=RED,
			stroke_width=2.5,
		)
		f_horizontal_line = DashedLine(
			plane.c2p(v_xy[0], v_xy[1]),
			plane.c2p(proj_horizontal_xy[0], proj_horizontal_xy[1]),
			color=RED,
			stroke_width=2.5,
		)

		# Place component labels outside the tile to reduce clutter.
		f_b1_label = Tex(r"f_{b_1}")
		f_b1_label.set_color(RED)
		f_b1_label.scale(0.66)
		f_b1_label.next_to(plane.c2p(proj_vertical_xy[0], proj_vertical_xy[1]), DOWN + RIGHT, buff=0.1)

		f_b2_label = Tex(r"f_{b_2}")
		f_b2_label.set_color(RED)
		f_b2_label.scale(0.66)
		f_b2_label.next_to(plane.c2p(proj_horizontal_xy[0], proj_horizontal_xy[1]), LEFT + UP, buff=0.1)

		f_b1_pair_tex = f"({(v_xy[0] - anchor_xy[0]):.2f},0)"
		f_b1_pair = Tex(f_b1_pair_tex)
		f_b1_pair.set_color(RED)
		f_b1_pair.scale(0.52)
		f_b1_pair.next_to(f_b1_label, RIGHT, buff=0.08)

		f_b2_pair_tex = f"(0,{(v_xy[1] - anchor_xy[1]):.2f})"
		f_b2_pair = Tex(f_b2_pair_tex)
		f_b2_pair.set_color(RED)
		f_b2_pair.scale(0.52)
		f_b2_pair.next_to(f_b2_label, LEFT, buff=0.08)

		self.play(ShowCreation(f_horizontal_line), ShowCreation(f_vertical_line), run_time=1.0)
		self.play(
			Write(f_b2_label),
			Write(f_b1_label),
			Write(f_b2_pair),
			Write(f_b1_pair),
			run_time=0.9,
		)

		# 9) Rewrite v's ordered pair with explicit token coloring (stable in ManimGL).
		tokens = [
			(Tex(r"v"), PURPLE),
			(Tex(r"("), WHITE),
			(Tex(r"v_{x_{b_1}}"), BLUE),
			(Tex(r"+"), WHITE),
			(Tex(r"f_{b_1}"), RED),
			(Tex(r","), WHITE),
			(Tex(r"v_{x_{b_2}}"), BLUE),
			(Tex(r"+"), WHITE),
			(Tex(r"f_{b_2}"), RED),
			(Tex(r")"), WHITE),
		]

		for mob, color in tokens:
			mob.set_color(color)
			mob.scale(0.62)

		v_repr_label = VGroup(*[mob for mob, _ in tokens])
		v_repr_label.arrange(RIGHT, buff=0.035, aligned_edge=DOWN)
		v_repr_label.next_to(v_point, UP + RIGHT, buff=0.12)
		self.play(ReplacementTransform(v_label, v_repr_label), run_time=1.1)
		self.wait(1.2)
