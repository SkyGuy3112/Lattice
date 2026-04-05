from manimlib import *


class TilingBoundaryIssue(Scene):
	def construct(self):
		self.camera.background_color = BLACK

		# 1) Grid, same styling as prior scenes.
		plane = NumberPlane(
			x_range=(-8, 8, 1),
			y_range=(-5, 5, 1),
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
		self.add(plane)

		origin = plane.c2p(0, 0)
		b1_end = plane.c2p(1, 0)
		b2_end = plane.c2p(0, 1)

		# 2) Basis B1 with same color format.
		b1_vec = Arrow(origin, b1_end, buff=0)
		b1_vec.set_color(MAROON)
		b1_vec.set_stroke(color=MAROON, opacity=1.0)

		b2_vec = Arrow(origin, b2_end, buff=0)
		b2_vec.set_color(TEAL)
		b2_vec.set_stroke(color=TEAL, opacity=1.0)

		self.play(ShowCreation(b1_vec), ShowCreation(b2_vec), run_time=1.2)

		# 3) Fundamental parallelepiped for B1 with solid completion edges.
		top_right = plane.c2p(1, 1)
		right_edge = Line(b1_end, top_right, color=YELLOW, stroke_width=3)
		top_edge = Line(b2_end, top_right, color=YELLOW, stroke_width=3)

		cell_fill = Polygon(origin, b1_end, top_right, b2_end, stroke_width=0)
		cell_fill.set_fill(YELLOW, opacity=0.12)

		cell_group = VGroup(cell_fill, right_edge, top_edge)
		self.play(FadeIn(cell_fill), ShowCreation(right_edge), ShowCreation(top_edge), run_time=1.2)

		# 4) Duplicate and translate the cell to the right neighbor.
		# Include the duplicate's left boundary so the shared edge is explicit.
		duplicate_left_edge = Line(origin, b2_end, color=YELLOW, stroke_width=3)
		duplicate_cell = VGroup(
			cell_fill.copy(),
			right_edge.copy(),
			top_edge.copy(),
			duplicate_left_edge,
		)
		self.add(duplicate_cell)
		shift_right = plane.c2p(1, 0) - origin
		self.play(duplicate_cell.animate.shift(shift_right), run_time=1.5)

		# 5) Highlight overlapped boundary edge in red.
		overlap_edge = Line(plane.c2p(1, 0), plane.c2p(1, 1), color=RED, stroke_width=7)
		self.play(
			right_edge.animate.set_stroke(RED, width=5),
			duplicate_cell[3].animate.set_stroke(RED, width=5),
			FadeIn(overlap_edge),
			run_time=1.0,
		)
		self.wait(1.5)
