# Copilot Instructions for This Repository

Use docs/animation_style_guide.md as the source of truth for animation style and workflow.

Required defaults unless user overrides:
- Preserve style identity: black background, gray semi-transparent grid, MAROON/TEAL basis vectors, YELLOW cell/highlight, WHITE calculation text.
- Preserve algorithm variable names: u, v, mu, c.
- Keep panel layout pinned: status top-left, algorithm top-right, table bottom-left.
- Keep 1 second pacing pauses between major algorithm steps.
- After code changes, render automatically.
- Render workflow must be:
  1) conda activate manim_env
  2) delete prior output and temp video
  3) run manimgl at 1920x1080

Project organization:
- Lattice scenes are in scenes/lattice/
- Physics scenes are in scenes/physics/
- Notebook artifacts are in notebooks/
