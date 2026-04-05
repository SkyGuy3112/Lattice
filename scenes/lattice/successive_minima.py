from manimlib import *
import numpy as np


class SuccessiveMinimaScene(Scene):
	def construct(self):
		self.camera.background_color = BLACK
		full_view_width = 30.0
		zoomed_view_width = 11.0
		self.camera.frame.set_width(full_view_width)

		# 1) Predrawn grid matching previous visual style.
		plane = NumberPlane(
			x_range=(-36, 36, 1),
			y_range=(-22, 22, 1),
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

		# Basis matrices from provided screenshot (column vectors).
		# B  = [[1,2],[1,0]]  => b1=(1,1), b2=(2,0)
		# B' = [[7,10],[3,4]] => b1'=(7,3), b2'=(10,4)
		anchor = np.array([0.0, 0.0])
		good_b1 = np.array([1.0, 1.0])
		good_b2 = np.array([2.0, 0.0])
		bad_b1 = np.array([7.0, 3.0])
		bad_b2 = np.array([10.0, 4.0])

		good_color = "#F48CFF"  # light magenta
		bad_color = "#8DF5B2"   # light green
		circle_color = BLUE

		def c2p(v):
			return plane.c2p(v[0], v[1])

		def basis_vectors(base, v1, v2, color):
			p0 = c2p(base)
			p1 = c2p(base + v1)
			p2 = c2p(base + v2)

			vec1 = Arrow(p0, p1, buff=0)
			vec1.set_color(color)
			vec1.set_stroke(color=color, width=4, opacity=1.0)

			vec2 = Arrow(p0, p2, buff=0)
			vec2.set_color(color)
			vec2.set_stroke(color=color, width=4, opacity=1.0)

			return VGroup(vec1, vec2)

		def fundamental_cell(base, v1, v2, color):
			p0 = c2p(base)
			p1 = c2p(base + v1)
			p2 = c2p(base + v1 + v2)
			p3 = c2p(base + v2)

			fill = Polygon(p0, p1, p2, p3, stroke_width=0)
			fill.set_fill(color, opacity=0.14)

			edges = VGroup(
				DashedLine(p0, p1, color=color, stroke_width=2.6),
				DashedLine(p1, p2, color=color, stroke_width=2.6),
				DashedLine(p2, p3, color=color, stroke_width=2.6),
				DashedLine(p3, p0, color=color, stroke_width=2.6),
			)
			return VGroup(fill, edges)

		def det2(u, v):
			return float(u[0] * v[1] - u[1] * v[0])

		# Predrawn bases on first frame.
		good_vectors = basis_vectors(anchor, good_b1, good_b2, good_color)
		bad_vectors = basis_vectors(anchor, bad_b1, bad_b2, bad_color)
		self.add(good_vectors, bad_vectors)

		# Optional compact labels for orientation.
		good_label = Tex("B")
		good_label.set_color(good_color)
		good_label.scale(0.7)
		good_label.next_to(c2p(anchor + 0.55 * (good_b1 + good_b2)), LEFT + DOWN, buff=0.12)

		bad_label = Tex("B'")
		bad_label.set_color(bad_color)
		bad_label.scale(0.7)
		bad_label.next_to(c2p(anchor + 0.55 * (bad_b1 + bad_b2)), UP, buff=0.12)
		self.add(good_label, bad_label)

		# 2) Animate both fundamental cells simultaneously.
		good_cell = fundamental_cell(anchor, good_b1, good_b2, good_color)
		bad_cell = fundamental_cell(anchor, bad_b1, bad_b2, bad_color)

		self.play(
			FadeIn(good_cell[0]),
			ShowCreation(good_cell[1]),
			FadeIn(bad_cell[0]),
			ShowCreation(bad_cell[1]),
			run_time=1.9,
		)

		# 1) Keep only bad basis/cell for successive minima phase.
		self.play(
			FadeOut(good_vectors),
			FadeOut(good_cell),
			FadeOut(good_label),
			run_time=0.9,
		)

		# 2) Precompute needed bad-basis tiles, then fade them in together.
		x_min, x_max = -36, 36
		y_min, y_max = -22, 22
		base_center = 0.5 * (bad_b1 + bad_b2)

		candidate_indices = []
		for i in range(-14, 15):
			for j in range(-14, 15):
				if (i, j) == (0, 0):
					continue

				center_xy = base_center + i * bad_b1 + j * bad_b2
				if x_min - 18 <= center_xy[0] <= x_max + 18 and y_min - 14 <= center_xy[1] <= y_max + 14:
					candidate_indices.append((i, j))

		candidate_indices.sort(key=lambda ij: (ij[0] ** 2 + ij[1] ** 2, abs(ij[1]), abs(ij[0])))

		tile_layer = VGroup()
		tile_groups = []
		for i, j in candidate_indices:
			shift_xy = i * bad_b1 + j * bad_b2
			shift_p = c2p(shift_xy) - c2p(np.array([0.0, 0.0]))

			tile_fill = bad_cell[0].copy()
			tile_fill.shift(shift_p)
			tile_fill.set_fill(bad_color, opacity=0.14)

			tile_edges = bad_cell[1].copy()
			tile_edges.shift(shift_p)

			tile_groups.append(VGroup(tile_fill, tile_edges))

		if tile_groups:
			tile_layer = VGroup(*tile_groups)
			self.play(FadeIn(tile_layer), run_time=1.4)

		# Show anchor points of bad-lattice tiles.
		all_anchor_indices = [(0, 0)] + candidate_indices
		all_anchor_indices.sort(key=lambda ij: (ij[0] ** 2 + ij[1] ** 2, abs(ij[1]), abs(ij[0])))

		anchor_dots = []
		for i, j in all_anchor_indices:
			pt = anchor + i * bad_b1 + j * bad_b2
			dot = Dot(c2p(pt), radius=0.045, color=bad_color)
			dot.set_fill(bad_color, opacity=0.95)
			dot.set_stroke(bad_color, width=0, opacity=1.0)
			anchor_dots.append(dot)
		anchor_dot_group = VGroup(*anchor_dots)

		if anchor_dots:
			self.play(FadeIn(anchor_dot_group), run_time=0.9)

		center = c2p(anchor)

		# Before circle animation, zoom in around the origin.
		self.play(
			self.camera.frame.animate.move_to(center).set_width(zoomed_view_width),
			run_time=1.1,
		)
		self.wait(1.0)

		# 3) Dashed blue circle with overlay starts only after zoom-in finishes.

		radius_tracker = ValueTracker(0.001)

		circle_fill = always_redraw(
			lambda: Circle(radius=radius_tracker.get_value()).move_to(center).set_stroke(width=0).set_fill(circle_color, opacity=0.08)
		)
		circle_outline = always_redraw(
			lambda: DashedVMobject(
				Circle(radius=radius_tracker.get_value()).move_to(center).set_stroke(circle_color, width=2.8, opacity=1.0),
				num_dashes=84,
			)
		)

		self.add(circle_fill, circle_outline)

		# Algorithmic successive minima over bad-basis lattice anchors.
		# Rules:
		# 1) lambda_i must lie on a strictly larger radius than lambda_{i-1}.
		# 2) Independence is checked via det([lambda_{i-1}, candidate]).
		vectors = []
		for i in range(-10, 11):
			for j in range(-10, 11):
				if i == 0 and j == 0:
					continue
				v = i * bad_b1 + j * bad_b2
				n = float(np.linalg.norm(v))
				vectors.append((i, j, v, n))

		vectors.sort(key=lambda item: (item[3], -item[2][1], -item[2][0]))

		# lambda_1: shortest nonzero vector
		lambda1_v, lambda1_r = vectors[0][2], vectors[0][3]

		# lambda_2: first candidate satisfying both conditions
		# (strictly larger radius and independent from lambda_1).
		eps = 1e-8
		lambda2_v = None
		lambda2_r = None
		for _, _, cand_v, cand_r in vectors[1:]:
			# Condition 1: must not lie on lambda_1 circle.
			if cand_r <= lambda1_r + eps:
				continue

			# Condition 2: determinant test with ordered vectors [lambda_1, candidate].
			if abs(det2(lambda1_v, cand_v)) > eps:
				lambda2_v = cand_v
				lambda2_r = cand_r
				break

		if lambda2_v is None:
			raise ValueError("Could not find lambda_2 satisfying radius and independence conditions.")

		def lambda_label(i, vec_xy, radius_value):
			point = c2p(anchor + vec_xy)
			u = vec_xy / np.linalg.norm(vec_xy)
			offset = np.array([u[0], u[1], 0.0]) * 0.55

			name = Tex(rf"\lambda_{i}")
			name.set_color(WHITE)
			name.scale(0.58)
			name.move_to(point + offset)

			length = Tex(f"{radius_value:.2f}")
			length.set_color(WHITE)
			length.scale(0.52)
			length.next_to(name, DOWN, buff=0.05)

			hit_dot = Dot(point, radius=0.055, color=BLUE)
			hit_dot.set_fill(BLUE, opacity=1.0)
			hit_dot.set_stroke(BLUE, width=0, opacity=1.0)

			return hit_dot, name, length

		hit1, lambda1, lambda1_len = lambda_label(1, lambda1_v, lambda1_r)
		hit2, lambda2, lambda2_len = lambda_label(2, lambda2_v, lambda2_r)

		# Grow to first intersection while starting a gradual zoom-out.
		self.play(
			radius_tracker.animate.set_value(lambda1_r),
			run_time=1.9,
			rate_func=linear,
		)
		self.play(FadeIn(hit1), FadeIn(lambda1), FadeIn(lambda1_len), run_time=0.35)

		# Continue to second intersection.
		self.play(
			radius_tracker.animate.set_value(lambda2_r),
			run_time=1.7,
			rate_func=linear,
		)
		self.play(FadeIn(hit2), FadeIn(lambda2), FadeIn(lambda2_len), run_time=0.35)

		# 1) Fade out bad tiles, bad basis, and bad fundamental cell.
		self.play(
			FadeOut(tile_layer),
			FadeOut(anchor_dot_group),
			FadeOut(bad_vectors),
			FadeOut(bad_cell),
			FadeOut(bad_label),
			run_time=1.0,
		)

		# 2) Fade in good basis and good fundamental cell again.
		self.play(
			FadeIn(good_vectors),
			FadeIn(good_cell),
			FadeIn(good_label),
			run_time=1.0,
		)

		# 3) Tile good-basis cell with circular (nearest-first) animation.
		good_tile_indices = []
		good_base_center = 0.5 * (good_b1 + good_b2)
		for i in range(-12, 13):
			for j in range(-12, 13):
				if (i, j) == (0, 0):
					continue
				center_xy = good_base_center + i * good_b1 + j * good_b2
				if x_min - 3 <= center_xy[0] <= x_max + 3 and y_min - 3 <= center_xy[1] <= y_max + 3:
					good_tile_indices.append((i, j))

		good_tile_indices.sort(key=lambda ij: (ij[0] ** 2 + ij[1] ** 2, abs(ij[1]), abs(ij[0])))

		good_tile_groups = []
		for i, j in good_tile_indices:
			shift_xy = i * good_b1 + j * good_b2
			shift_p = c2p(shift_xy) - c2p(np.array([0.0, 0.0]))

			tile_fill = good_cell[0].copy()
			tile_fill.shift(shift_p)
			tile_fill.set_fill(good_color, opacity=0.0)

			tile_edges = good_cell[1].copy()
			tile_edges.shift(shift_p)
			for edge in tile_edges:
				edge.set_stroke(opacity=0.0)

			good_tile_groups.append(VGroup(tile_fill, tile_edges))

		if good_tile_groups:
			self.add(*good_tile_groups)
			self.play(
				LaggedStart(
					*[
						AnimationGroup(
							tile[0].animate.set_fill(opacity=0.14),
							*[edge.animate.set_stroke(opacity=1.0) for edge in tile[1]],
						)
						for tile in good_tile_groups
					],
					lag_ratio=0.02,
				),
				run_time=3.8,
			)

		# 4) Fade out minima circle while keeping found points.
		self.play(
			circle_fill.animate.set_fill(opacity=0.0),
			circle_outline.animate.set_stroke(opacity=0.0),
			run_time=0.9,
		)
		self.remove(circle_fill, circle_outline)

		self.wait(1.1)


class Successive_minima(SuccessiveMinimaScene):
	pass
