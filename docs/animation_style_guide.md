# Lattice Animation Style Guide

This document is the canonical handoff for future animation sessions in this repository.

## 1) Visual Identity
- Background: black.
- Grid: NumberPlane with semi-transparent gray lines and axes.
  - background line stroke width about 1.15 to 1.2
  - background line opacity about 0.28 to 0.30
  - axis stroke width about 1.8 to 2.0
  - axis opacity about 0.45 to 0.50
- Basis vector colors:
  - u / b1: MAROON
  - v / b2: TEAL
- Cell and highlight color: YELLOW.
- Main explanatory text color: WHITE.

## 2) Composition Rules
- Keep algorithm panel in top-right corner.
- Keep current vector-values panel in top-left corner.
- If a table is present, keep it pinned bottom-left.
- Maintain enough margins from frame edges to avoid clipping in 1080p exports.

## 3) Animation Flow Rules
- Introduce scene in this order:
  1. basis vectors
  2. fundamental cell
  3. panels
- For algorithm loops:
  1. highlight current step
  2. show calculations
  3. apply geometric/vector update
  4. update panel values
  5. then append table row (if table variant)
- Include a 1 second pause between major step transitions.

## 4) Algorithm Naming Convention
- Preserve variable names used in algorithm text and scenes:
  - u, v, mu, c
- Do not rename to alternate symbols unless explicitly requested.

## 5) Rendering Workflow
- Environment: conda, env name manim_env.
- Always remove previous output video before render to avoid stale/glitched output.
- Default command template:
  - conda activate manim_env && rm -f videos/<SceneName>.mp4 videos/<SceneName>_temp.mp4 && manimgl <path-to-scene-file>.py <SceneName> -o -r 1920x1080

## 6) Scene File Locations
- Lattice scenes: scenes/lattice/
- Physics scenes: scenes/physics/

## 7) Future Session Handoff
When starting a new session, reference this file and ask the assistant to follow it exactly.
Recommended opener:
- "Use docs/animation_style_guide.md as the source of truth for style, pacing, colors, panel layout, and rendering workflow."
