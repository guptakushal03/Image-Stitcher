# Image Stitcher

Stitch two overlapping images into a single panoramic image using OpenCV!
Use either the **Command-Line Interface (CLI)** or a **Graphical User Interface (GUI)** built with Tkinter.

---

## Features

* Automatic image stitching using OpenCV
* Dual support: CLI for power users, GUI for ease of use
* Graceful error handling with helpful tips
* Supports `.png`, `.jpg`, `.jpeg`, etc.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/guptakushal03/image-stitcher.git
cd image-stitcher
```

2. Install the required dependencies:

```bash
pip install opencv-python
```

---

## How It Works

* Uses OpenCV’s `Stitcher` class (`cv2.Stitcher_create()`) to automatically find keypoints and blend images.
* Designed to stitch **two** horizontally overlapping images.
* Output is saved as a new image.

---

## Usage

### CLI Mode

```bash
python image_stitcher.py image1.jpg image2.jpg output.jpg
```

Example:

```bash
python image_stitcher.py left.png right.png result.png
```

### GUI Mode

Launch the graphical interface using:

```bash
python image_stitcher.py --gui
```

A window will appear allowing you to select two images and choose where to save the result.

---

## Example

Before:

* `image1.jpg`
* `image2.jpg` *(with overlapping region)*

After:

* `output.jpg` *(a stitched panoramic view)*

---

## Troubleshooting

* Make sure both images exist and have overlapping regions.
* Images should be of reasonable resolution and not blank.
* If stitching fails, try flipping the order of images or check that they’re aligned horizontally.

---

## Tech Stack

* **Python**
* **OpenCV** (for stitching)
* **Tkinter** (for GUI)
