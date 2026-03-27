from manimlib import *


class TilingTrueB2(Scene):
	def construct(self):
		self.camera.background_color = BLACK

		# 1) Pre-drawn grid and ordered basis B2 = {(2,0), (1,1)}.
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
		b1_end = plane.c2p(2, 0)
		b2_end = plane.c2p(1, 1)
		top_right = plane.c2p(3, 1)

		b1_vec = Arrow(origin, b1_end, buff=0)
		b1_vec.set_color(MAROON)
		b1_vec.set_stroke(color=MAROON, opacity=1.0)

		b2_vec = Arrow(origin, b2_end, buff=0)
		b2_vec.set_color(TEAL)
		b2_vec.set_stroke(color=TEAL, opacity=1.0)

		self.add(plane, b1_vec, b2_vec)

		# 2) Dashed completion edges for the fundamental parallelepiped.
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

		shift_b1 = b1_end - origin
		shift_b2 = b2_end - origin

		# 3) Prepare lattice anchors, then reveal yellow points immediately.
		x_min, x_max = -10, 10
		y_min, y_max = -6, 6
		base_center = np.array([1.5, 0.5, 0.0])

		candidate_indices = []
		for i in range(-9, 10):
			for j in range(-8, 9):
				if (i, j) in [(0, 0), (1, 0)]:
					continue

				center = base_center + i * np.array([2.0, 0.0, 0.0]) + j * np.array([1.0, 1.0, 0.0])
				if x_min - 2 <= center[0] <= x_max + 2 and y_min - 1 <= center[1] <= y_max + 1:
					candidate_indices.append((i, j))

		all_anchor_indices = [(0, 0), (1, 0)] + candidate_indices
		all_anchor_indices.sort(key=lambda ij: (ij[0] ** 2 + ij[1] ** 2, abs(ij[1]), abs(ij[0])))

		anchor_dots = []
		for i, j in all_anchor_indices:
			dot = Dot(origin + i * shift_b1 + j * shift_b2, radius=0.045, color=YELLOW)
			dot.set_fill(YELLOW, opacity=0.0)
			dot.set_stroke(YELLOW, width=0, opacity=0.0)
			anchor_dots.append(dot)

		if anchor_dots:
			self.add(*anchor_dots)
			self.play(
				LaggedStart(
					*[dot.animate.set_fill(YELLOW, opacity=1.0) for dot in anchor_dots],
					lag_ratio=0.02,
				),
				run_time=2.8,
			)

		# 4) Duplicate and translate right so boundaries meet at x=2.
		duplicate_cell = fundamental_cell.copy()
		self.add(duplicate_cell)
		self.play(duplicate_cell.animate.shift(shift_b1), run_time=1.3)

		# 5) Distance-ordered per-cell fade tiling to cover the visible span.
		# Nearest cells fade first, then progressively farther ones.
		candidate_indices.sort(key=lambda ij: (ij[0] ** 2 + ij[1] ** 2, abs(ij[1]), abs(ij[0])))

		tile_groups = []
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

			tile_groups.append(VGroup(tile_fill, tile_edge_b1, tile_edge_b2))

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
		self.wait(1.0)
