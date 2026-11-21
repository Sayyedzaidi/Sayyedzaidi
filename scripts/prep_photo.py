#!/usr/bin/env python3
"""
Prepares the user portrait for crisp, high-definition ASCII rendering:
  1. Crops directly to the head and shoulders, eliminating distracting pillars / walls.
  2. Uses AI segmentation (u2netp) to isolate the subject from the background.
  3. Applies bilateral smoothing to reduce noise while maintaining sharp contours.
  4. Enhances edge contrast (Difference of Gaussians) so eyes, hair, and facial lines pop.
  5. Composites onto a pure white canvas (which translates to transparent space in ASCII).
"""
import os
import sys
import cv2
import numpy as np
from PIL import Image
import rembg

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

session = rembg.new_session("u2netp")
im = Image.open(INP)

# Crop to head/face area (140 to 370 x, 110 to 370 y in 460px scale)
head = im.crop((140, 110, 370, 370))
cut = rembg.remove(head, session=session)

rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])

# Smooth texture, keep strong edges
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
smooth = gray
for _ in range(3):
    smooth = cv2.bilateralFilter(smooth, 7, 30, 7)

# Contrast stretch over face area
mask = alpha > 40
lo, hi = np.percentile(smooth[mask], [3, 90])
tone = np.clip((smooth.astype(np.float32) - lo) / (hi - lo), 0, 1)

# Difference of Gaussians edge sharpening
fine = cv2.GaussianBlur(smooth, (0, 0), 1.2).astype(np.float32)
coarse = cv2.GaussianBlur(smooth, (0, 0), 5.0).astype(np.float32)
edges = np.clip((coarse - fine) / 35.0, 0, 1)

# Darkened line ridges + crisp tones
out = np.clip(tone - 0.75 * edges, 0, 1) * 255
alpha_f = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
out = out * alpha_f + 255.0 * (1.0 - alpha_f)

canvas = np.full((400, 400), 255, np.uint8)
h, w = out.shape
canvas[20:20+h, 20:20+w] = out.astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print(f"wrote {OUT}: {canvas.shape}")
