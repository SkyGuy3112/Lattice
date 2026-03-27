from manimlib import *
import numpy as np


class LLLLatticeReduction3D(ThreeDScene):
	def construct(self):
		self.camera.background_color = BLACK
		iso_phi = 55 * DEGREES
		iso_theta = -45 * DEGREES
		frame = self.camera.frame
		if hasattr(self, "set_camera_orientation"):
			self.set_camera_orientation(phi=iso_phi, theta=iso_theta, distance=7)
		elif hasattr(frame, "reorient"):
			frame.reorient(-45, 55)
			frame.set_height(9)
		elif hasattr(frame, "set_euler_angles"):
			frame.set_euler_angles(theta=iso_theta, phi=iso_phi)
			frame.set_height(9)

		def move_camera_view(theta_deg, phi_deg, height=9, run_time=1.0):
			if hasattr(frame, "animate") and hasattr(frame, "reorient"):
				anim = frame.animate.reorient(theta_deg, phi_deg)
				if hasattr(frame, "set_height"):
					anim = anim.set_height(height)
				self.play(anim, run_time=run_time)
			else:
				if hasattr(frame, "reorient"):
					frame.reorient(theta_deg, phi_deg)
				if hasattr(frame, "set_height"):
					frame.set_height(height)

		def pin_to_screen(*mobs):
			for mob in mobs:
				if hasattr(mob, "fix_in_frame"):
					mob.fix_in_frame()
			if hasattr(self, "add_fixed_in_frame_mobjects"):
				self.add_fixed_in_frame_mobjects(*mobs)
			elif hasattr(self.camera, "add_fixed_in_frame_mobjects"):
				self.camera.add_fixed_in_frame_mobjects(*mobs)

		def face_camera(*mobs):
			for mob in mobs:
				if hasattr(mob, "fix_orientation"):
					mob.fix_orientation()
			if hasattr(self, "add_fixed_orientation_mobjects"):
				self.add_fixed_orientation_mobjects(*mobs)
			elif hasattr(self.camera, "add_fixed_orientation_mobjects"):
				self.camera.add_fixed_orientation_mobjects(*mobs)

		# 3D Cartesian frame
		axes = ThreeDAxes(
			x_range=(-6, 6, 1),
			y_range=(-6, 6, 1),
			z_range=(-6, 6, 1),
			axis_config={
				"color": GREY,
				"stroke_opacity": 0.6,
				"stroke_width": 2,
			},
		)
		self.play(ShowCreation(axes))

		c1 = TEAL
		c2 = MAROON
		c3 = GOLD
		delta = 0.75

		B = np.array(
			[
				[4.0, 1.0, 1.0],
				[1.0, 3.0, 1.0],
				[1.0, 1.0, 2.0],
			],
			dtype=float,
		)

		def vec_str(v):
			return f"({int(round(v[0]))}, {int(round(v[1]))}, {int(round(v[2]))})"

		def basis_arrow(v, color=WHITE):
			return Arrow(ORIGIN, np.array([v[0], v[1], v[2]]), buff=0, color=color)

		def build_basis_visual(basis):
			group = VGroup()
			for i in range(3):
				arr = basis_arrow(basis[i], color=WHITE)
				tip = Dot(arr.get_end(), color=WHITE, radius=0.05)
				group.add(arr, tip)
			return group

		def build_moving_vector_labels(vector_group):
			directions = [RIGHT + UP, LEFT + UP, RIGHT + DOWN]
			colors = [c1, c2, c3]
			labels = VGroup()
			for i in range(3):
				arr = vector_group[2 * i]
				label = Tex(f"b_{i + 1}").set_color(colors[i])

				def update_label(m, a=arr, d=directions[i]):
					m.next_to(a.get_end(), d, buff=0.12)

				label.add_updater(update_label)
				update_label(label)
				labels.add(label)
			face_camera(*labels)
			return labels

		def build_side_vectors(basis):
			colors = [c1, c2, c3]
			group = VGroup()
			for i in range(3):
				arr = Arrow(ORIGIN, basis[i], buff=0, color=colors[i], stroke_width=5)
				group.add(arr)
			return group

		def build_basis_text(basis):
			lines = VGroup(
				Tex(f"b_1 = {vec_str(basis[0])}").set_color(c1),
				Tex(f"b_2 = {vec_str(basis[1])}").set_color(c2),
				Tex(f"b_3 = {vec_str(basis[2])}").set_color(c3),
			)
			return lines.arrange(DOWN, aligned_edge=LEFT).to_corner(UL).shift(DOWN * 0.4)

		def build_parallelepiped_wireframe(basis, color=BLUE):
			b1, b2, b3 = basis[0], basis[1], basis[2]
			verts = [
				np.array([0.0, 0.0, 0.0]),
				b1,
				b2,
				b3,
				b1 + b2,
				b1 + b3,
				b2 + b3,
				b1 + b2 + b3,
			]
			edges = [
				(0, 1), (0, 2), (0, 3),
				(1, 4), (1, 5),
				(2, 4), (2, 6),
				(3, 5), (3, 6),
				(4, 7), (5, 7), (6, 7),
			]
			return VGroup(*[
				Line(verts[i], verts[j], color=color, stroke_opacity=0.9, stroke_width=3)
				for i, j in edges
			])

		def gram_schmidt(basis):
			n = basis.shape[0]
			b_star = np.zeros_like(basis, dtype=float)
			mu = np.zeros((n, n), dtype=float)
			for i in range(n):
				b_star[i] = basis[i].copy()
				for j in range(i):
					denom = np.dot(b_star[j], b_star[j])
					if np.isclose(denom, 0.0):
						continue
					mu[i, j] = np.dot(basis[i], b_star[j]) / denom
					b_star[i] = b_star[i] - mu[i, j] * b_star[j]
			return b_star, mu

		def estimate_outer_iterations(basis, delta_val=0.75, max_steps_val=50):
			B_sim = basis.copy().astype(float)
			n_sim = B_sim.shape[0]
			k_sim = 1
			steps_sim = 0
			while k_sim < n_sim and steps_sim < max_steps_val:
				steps_sim += 1
				b_star_sim, mu_sim = gram_schmidt(B_sim)
				for j_sim in range(k_sim - 1, -1, -1):
					m_sim = int(round(mu_sim[k_sim, j_sim]))
					if m_sim != 0:
						B_sim[k_sim] = B_sim[k_sim] - m_sim * B_sim[j_sim]

				b_star_sim, mu_sim = gram_schmidt(B_sim)
				lhs_sim = np.dot(b_star_sim[k_sim], b_star_sim[k_sim])
				rhs_sim = (delta_val - mu_sim[k_sim, k_sim - 1] ** 2) * np.dot(
					b_star_sim[k_sim - 1],
					b_star_sim[k_sim - 1],
				)
				if lhs_sim >= rhs_sim - 1e-9:
					k_sim += 1
				else:
					B_sim[[k_sim - 1, k_sim]] = B_sim[[k_sim, k_sim - 1]]
					k_sim = max(k_sim - 1, 1)
			return max(steps_sim, 1)

		basis_visual = build_basis_visual(B)
		moving_labels = build_moving_vector_labels(basis_visual)
		info_text = build_basis_text(B)
		basis_legend = VGroup(
			Tex("b_1").set_color(c1),
			Tex("b_2").set_color(c2),
			Tex("b_3").set_color(c3),
		).arrange(RIGHT, buff=0.4).to_corner(UR).shift(DOWN * 0.4)
		pin_to_screen(info_text, basis_legend)
		self.play(ShowCreation(basis_visual), Write(info_text))
		self.play(Write(moving_labels))
		self.play(Write(basis_legend))
		self.wait(0.5)

		# Stage 1: Fundamental cell before reduction
		# Move from isometric into a more top-leaning view to inspect the cell.
		move_camera_view(theta_deg=-30, phi_deg=70, height=8.2, run_time=1.2)
		before_cell = build_parallelepiped_wireframe(B, color=BLUE)
		before_side_vectors = build_side_vectors(B)
		before_caption = Text("Fundamental cell (before reduction)", font_size=28, color=BLUE)
		before_caption.to_edge(DOWN)
		pin_to_screen(before_caption)
		self.play(ShowCreation(before_cell), ShowCreation(before_side_vectors), FadeIn(before_caption, UP))
		self.wait(1)
		self.play(FadeOut(before_cell), FadeOut(before_side_vectors), FadeOut(before_caption))

		# Reframe for the iterative LLL updates.
		move_camera_view(theta_deg=-45, phi_deg=55, height=8.8, run_time=1.0)
		loop_start_theta = -45.0
		loop_end_theta = loop_start_theta + 90.0
		total_outer_iters = estimate_outer_iterations(B, delta_val=delta, max_steps_val=50)

		# Stage 2: LLL reduction loop
		action_text = Text("", font_size=24, color=YELLOW).to_edge(DOWN)
		pin_to_screen(action_text)

		n = 3
		k = 1
		steps = 0
		max_steps = 50

		while k < n and steps < max_steps:
			steps += 1
			progress = min(1.0, steps / total_outer_iters)
			theta_now = loop_start_theta + 90.0 * progress
			move_camera_view(theta_deg=theta_now, phi_deg=55, height=8.8, run_time=0.35)
			b_star, mu = gram_schmidt(B)

			# Size reduction: b_k <- b_k - round(mu_kj) b_j
			for j in range(k - 1, -1, -1):
				m = int(round(mu[k, j]))
				if m != 0:
					new_action = Text(
						f"Size reduction: b_{k + 1} <- b_{k + 1} - ({m}) b_{j + 1}",
						font_size=24,
						color=YELLOW,
					).to_edge(DOWN)
					pin_to_screen(new_action)
					self.play(ReplacementTransform(action_text, new_action))
					action_text = new_action

					B[k] = B[k] - m * B[j]

					new_basis_visual = build_basis_visual(B)
					new_moving_labels = build_moving_vector_labels(new_basis_visual)
					new_info_text = build_basis_text(B)
					pin_to_screen(new_info_text)
					self.play(
						ReplacementTransform(basis_visual, new_basis_visual),
						ReplacementTransform(moving_labels, new_moving_labels),
						ReplacementTransform(info_text, new_info_text),
					)
					basis_visual = new_basis_visual
					moving_labels = new_moving_labels
					info_text = new_info_text
					self.wait(0.3)

			b_star, mu = gram_schmidt(B)
			lhs = np.dot(b_star[k], b_star[k])
			rhs = (delta - mu[k, k - 1] ** 2) * np.dot(b_star[k - 1], b_star[k - 1])

			if lhs >= rhs - 1e-9:
				new_action = Text(
					f"Lovasz holds for k={k + 1}; increment k",
					font_size=24,
					color=GREEN,
				).to_edge(DOWN)
				pin_to_screen(new_action)
				self.play(ReplacementTransform(action_text, new_action))
				action_text = new_action
				self.wait(0.3)
				k += 1
			else:
				new_action = Text(
					f"Lovasz fails; swap b_{k} and b_{k + 1}",
					font_size=24,
					color=RED,
				).to_edge(DOWN)
				pin_to_screen(new_action)
				self.play(ReplacementTransform(action_text, new_action))
				action_text = new_action

				B[[k - 1, k]] = B[[k, k - 1]]

				new_basis_visual = build_basis_visual(B)
				new_moving_labels = build_moving_vector_labels(new_basis_visual)
				new_info_text = build_basis_text(B)
				pin_to_screen(new_info_text)
				self.play(
					ReplacementTransform(basis_visual, new_basis_visual),
					ReplacementTransform(moving_labels, new_moving_labels),
					ReplacementTransform(info_text, new_info_text),
				)
				basis_visual = new_basis_visual
				moving_labels = new_moving_labels
				info_text = new_info_text
				self.wait(0.3)
				k = max(k - 1, 1)

		self.play(FadeOut(action_text))
		move_camera_view(theta_deg=loop_end_theta, phi_deg=55, height=8.8, run_time=0.4)

		# Stage 3: Fundamental cell after reduction
		move_camera_view(theta_deg=-32, phi_deg=68, height=8.0, run_time=1.0)
		after_cell = build_parallelepiped_wireframe(B, color=GREEN)
		after_side_vectors = build_side_vectors(B)
		after_caption = Text("Fundamental cell (after reduction)", font_size=28, color=GREEN)
		after_caption.to_edge(DOWN)
		pin_to_screen(after_caption)
		self.play(ShowCreation(after_cell), ShowCreation(after_side_vectors), FadeIn(after_caption, UP))
		self.wait(1.5)
		self.play(FadeOut(after_cell), FadeOut(after_side_vectors), FadeOut(after_caption))

		final_text = Text("LLL-reduced basis", font_size=36, color=GREEN, font="Times New Roman")
		final_text.to_edge(RIGHT)
		pin_to_screen(final_text)
		self.play(Write(final_text))
		self.wait(2)
