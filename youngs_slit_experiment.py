from manimlib import *


class YoungsDoubleSlitInitial(Scene):
	def construct(self):
		self.camera.background_color = BLACK

		# Scene geometry in world coordinates
		source_point = np.array([-5.6, 0.0, 0.0])
		barrier_x = -1.6
		screen_x = 4.8
		slit_half_sep = 0.9
		slit_half_height = 0.2

		slit_top = np.array([barrier_x, slit_half_sep, 0.0])
		slit_bottom = np.array([barrier_x, -slit_half_sep, 0.0])

		# Physical parameters mapped into scene units
		wavelength = 0.55
		wave_speed = 1.25
		period = wavelength / wave_speed

		title = Text("Young's Double-Slit Experiment", font_size=40, color=WHITE)
		title.to_edge(UP)

		source = Dot(source_point, radius=0.08, color=YELLOW)
		source_label = Tex(r"\text{Coherent source}", color=YELLOW).scale(0.6)
		source_label.next_to(source, DOWN, buff=0.2)

		barrier_segments = VGroup(
			Line([barrier_x, -3.3, 0], [barrier_x, -slit_half_sep - slit_half_height, 0], color=GREY_B),
			Line([barrier_x, -slit_half_sep + slit_half_height, 0], [barrier_x, slit_half_sep - slit_half_height, 0], color=GREY_B),
			Line([barrier_x, slit_half_sep + slit_half_height, 0], [barrier_x, 3.3, 0], color=GREY_B),
		)
		barrier_segments.set_stroke(width=8)

		slit_markers = VGroup(
			Dot(slit_top, radius=0.03, color=TEAL),
			Dot(slit_bottom, radius=0.03, color=TEAL),
		)

		screen = Line([screen_x, -3.2, 0], [screen_x, 3.2, 0], color=BLUE_D)
		screen.set_stroke(width=6)

		incoming_beam = Arrow(source_point + RIGHT * 0.2, [barrier_x - 0.2, 0, 0], buff=0)
		incoming_beam.set_color(YELLOW)
		incoming_beam.set_stroke(width=5)

		apparatus = VGroup(source, barrier_segments, slit_markers, screen)

		self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)
		self.play(ShowCreation(apparatus), Write(source_label), run_time=1.8)
		self.play(GrowArrow(incoming_beam), run_time=1.0)

		time_tracker = ValueTracker(0.0)

		def make_wavefronts(slit_center, color):
			return always_redraw(
				lambda: VGroup(
					*[
						Circle(radius=r, arc_center=slit_center)
						.set_stroke(color=color, width=2.2, opacity=max(0.0, 0.9 - 0.14 * r))
						.set_fill(opacity=0)
						for r in [wave_speed * (time_tracker.get_value() - k * period) for k in range(20)]
						if 0.05 < r < 7.0
					]
				)
			)

		waves_top = make_wavefronts(slit_top, TEAL)
		waves_bottom = make_wavefronts(slit_bottom, MAROON)

		self.add(waves_top, waves_bottom)
		self.play(time_tracker.animate.set_value(5.5), run_time=5.5, rate_func=linear)

		# Build a vertical set of tiny emitters on the screen whose opacity follows I(y).
		ys = np.linspace(-2.8, 2.8, 90)
		screen_dots = VGroup()
		for y in ys:
			dot = Dot(np.array([screen_x - 0.02, y, 0.0]), radius=0.028, color=YELLOW)
			dot.set_fill(YELLOW, opacity=0.0)
			dot.set_stroke(YELLOW, width=0.0, opacity=0.0)
			screen_dots.add(dot)

		for dot, y in zip(screen_dots, ys):
			def updater(mob, dt, y=y):
				screen_point = np.array([screen_x, y, 0.0])
				r1 = np.linalg.norm(screen_point - slit_top)
				r2 = np.linalg.norm(screen_point - slit_bottom)
				phase = TAU * (r2 - r1) / wavelength
				interference = 0.5 * (1.0 + np.cos(phase))
				envelope = np.exp(-0.45 * (y ** 2))
				buildup = min(1.0, time_tracker.get_value() / 7.0)
				opacity = 0.05 + 0.95 * buildup * interference * envelope
				mob.set_fill(YELLOW, opacity=opacity)
				mob.set_stroke(YELLOW, width=0.0, opacity=0.0)

			dot.add_updater(updater)

		screen_label = Tex(r"\text{Detection screen}", color=BLUE_C).scale(0.58)
		screen_label.next_to(screen, RIGHT, buff=0.2)

		self.add(screen_dots)
		self.play(Write(screen_label), run_time=0.8)
		self.play(time_tracker.animate.set_value(8.0), run_time=2.6, rate_func=linear)

		# Dot-by-dot detection buildup sampled from the same intensity profile.
		p = []
		for y in ys:
			screen_point = np.array([screen_x, y, 0.0])
			r1 = np.linalg.norm(screen_point - slit_top)
			r2 = np.linalg.norm(screen_point - slit_bottom)
			phase = TAU * (r2 - r1) / wavelength
			interference = 0.5 * (1.0 + np.cos(phase))
			envelope = np.exp(-0.45 * (y ** 2))
			p.append(max(1e-6, interference * envelope))

		prob = np.array(p)
		prob = prob / prob.sum()

		np.random.seed(7)
		hit_ys = np.random.choice(ys, size=180, p=prob)
		hits = VGroup()
		for y in hit_ys:
			hit = Dot(np.array([screen_x - 0.08, y, 0.0]), radius=0.016, color=WHITE)
			hit.set_fill(WHITE, opacity=0.0)
			hit.set_stroke(WHITE, width=0.0, opacity=0.0)
			hits.add(hit)

		self.add(hits)
		self.play(
			LaggedStart(
				*[dot.animate.set_fill(WHITE, opacity=0.95) for dot in hits],
				lag_ratio=0.015,
			),
			run_time=4.2,
		)

		rel = Tex(r"d\sin\theta = m\lambda", color=WHITE).scale(0.62)
		rel.to_corner(DOWN + LEFT).shift(0.3 * UP + 0.3 * RIGHT)
		self.play(Write(rel), run_time=0.8)
		self.play(time_tracker.animate.increment_value(1.8), run_time=1.8, rate_func=linear)
		self.wait(1.0)
