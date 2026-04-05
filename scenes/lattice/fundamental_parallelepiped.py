from manimlib import *


class FundamentalParallelepipedExample(Scene):
	def construct(self):
		self.camera.background_color = BLACK

		# 1) Pre-drawn 2D grid with the same styling as previous scene.
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

		# 2) Basis for B2 = [[2, 1], [0, 1]] => b1=(2,0), b2=(1,1)
		origin = plane.c2p(0, 0)
		b1 = plane.c2p(2, 0)
		b2 = plane.c2p(1, 1)
		b12 = plane.c2p(3, 1)

		b1_vec = Arrow(origin, b1, buff=0)
		b1_vec.set_color(MAROON)
		b1_vec.set_stroke(color=MAROON, opacity=1.0)

		b2_vec = Arrow(origin, b2, buff=0)
		b2_vec.set_color(TEAL)
		b2_vec.set_stroke(color=TEAL, opacity=1.0)

		b1_label = Tex("(2,0)").set_color(WHITE).next_to(b1, DOWN, buff=0.12)
		b2_label = Tex("(1,1)").set_color(WHITE).next_to(b2, LEFT + UP, buff=0.12)

		self.play(
			ShowCreation(b1_vec),
			ShowCreation(b2_vec),
			Write(b1_label),
			Write(b2_label),
			run_time=1.6,
		)
		self.wait(0.3)

		# 3) Dashed completion edges of the fundamental parallelepiped (2D cell).
		edge_from_b1 = DashedLine(b1, b12, color=YELLOW)
		edge_from_b2 = DashedLine(b2, b12, color=YELLOW)
		self.play(ShowCreation(edge_from_b1), ShowCreation(edge_from_b2), run_time=1.1)

		# 4) Overlay the area of the fundamental parallelepiped.
		cell_fill = Polygon(origin, b1, b12, b2, stroke_width=0)
		cell_fill.set_fill(YELLOW, opacity=0.0)
		self.add(cell_fill)
		self.play(cell_fill.animate.set_fill(opacity=0.12), run_time=1.2)
		self.wait(1.2)
