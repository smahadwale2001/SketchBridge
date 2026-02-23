# SketchBridge Precision

**SketchBridge** is a high-precision digital-to-physical image tiling tool designed for artists, muralists, and drafters. It allows you to project and trace large-scale artworks using a standard laptop screen by breaking images into perfectly aligned, overlapping tiles.

Unlike standard image splitters, **SketchBridge** uses a **Global Anchor System**, ensuring that registration marks stay mathematically consistent across every tile, eliminating "drift" when moving your paper.

## ✨ Key Features

* **Global Registration Marks:** Anchor points are calculated based on the entire canvas. A point on the right of Tile A aligns perfectly with the same point on the left of Tile B.
* **5-Point "Tripod" Alignment:** Each tile features four corner anchors and one center anchor to prevent rotation and tilt errors.
* **Real-World Scaling:** Input your physical canvas and screen dimensions (in inches) to maintain a perfect 1:1 scale without image stretching.
* **Precision Geometry Controls:** * **Thickness Slider:** Adjust the pixel weight of trace points.
    * **Span Slider:** Control the physical length/height of crosshair arms.
    * **Color Picker:** Change point colors to contrast with your specific artwork.
* **High-Resolution Slicing:** Internal processing at high-res ensures your sketch lines stay sharp.
* **Async Processing:** Built-in loading states and threading to handle heavy image calculations without UI freezing.

## 🚀 How to Use

1. **Set Dimensions:** Enter your physical canvas size (e.g., 48" x 36") and your laptop's screen size.
2. **Configure Points:** Choose a high-contrast color and adjust the thickness/span of the anchors.
3. **Upload & Crop:** Load your image and select the specific area you want to tile.
4. **Start Tracing:** * Click **START TRACING** to enter fullscreen mode.
    * Trace the artwork **and** the 5 registration points.
    * Use **Arrow Keys** to move tiles. Align your previous paper points with the new screen points.
5. **Save Tiles:** Export all segments as high-quality PNGs for offline use.

## 🛠️ Requirements

* Python 3.x
* Pillow (PIL)

```bash
pip install Pillow