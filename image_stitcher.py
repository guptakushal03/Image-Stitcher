import cv2
import numpy as np
import argparse
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Union

class ImageStitcherPlugin:
    
    def __init__(self):
        self.orb = cv2.ORB_create(nfeatures=2000)
        self.bf = cv2.BFMatcher_create(cv2.NORM_HAMMING)
        self.match_ratio = 0.6
        self.min_match_count = 10

    def _load_image(self, image_path: str) -> np.ndarray:
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}. Make sure it's a valid image file (e.g., PNG, JPG).")
        return img

    def _detect_and_compute(self, img: np.ndarray) -> tuple[list[cv2.KeyPoint], np.ndarray]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        return keypoints, descriptors

    def _filter_matches(self, matches: list[tuple[cv2.DMatch, cv2.DMatch]]) -> list[cv2.DMatch]:
        good = []
        for m, n in matches:
            if m.distance < self.match_ratio * n.distance:
                good.append(m)
        return good

    def _warp_images(self, img1: np.ndarray, img2: np.ndarray, H: np.ndarray) -> np.ndarray:
        rows1, cols1 = img1.shape[:2]
        rows2, cols2 = img2.shape[:2]

        list_of_points_1 = np.float32([[0, 0], [0, rows1], [cols1, rows1], [cols1, 0]]).reshape(-1, 1, 2)
        temp_points = np.float32([[0, 0], [0, rows2], [cols2, rows2], [cols2, 0]]).reshape(-1, 1, 2)
        list_of_points_2 = cv2.perspectiveTransform(temp_points, H)
        list_of_points = np.concatenate((list_of_points_1, list_of_points_2), axis=0)

        [x_min, y_min] = np.int32(list_of_points.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(list_of_points.max(axis=0).ravel() + 0.5)
        translation_dist = [-x_min, -y_min]
        H_translation = np.array([[1, 0, translation_dist[0]], [0, 1, translation_dist[1]], [0, 0, 1]])

        output_img = cv2.warpPerspective(img2, H_translation.dot(H), (x_max - x_min, y_max - y_min))
        output_img[translation_dist[1]:rows1 + translation_dist[1], translation_dist[0]:cols1 + translation_dist[0]] = img1

        return output_img

    def stitch(self, image1_path: str, image2_path: str, output_path: str) -> None:
        try:
            img1 = self._load_image(image1_path)
            img2 = self._load_image(image2_path)

            keypoints1, descriptors1 = self._detect_and_compute(img1)
            keypoints2, descriptors2 = self._detect_and_compute(img2)

            if descriptors1 is None or descriptors2 is None:
                raise ValueError("Could not find enough details in one or both images. Try images with more distinct features.")

            matches = self.bf.knnMatch(descriptors1, descriptors2, k=2)
            good_matches = self._filter_matches(matches)

            if len(good_matches) < self.min_match_count:
                raise ValueError("The images don't have enough similar parts to stitch. Try images with more overlap.")

            src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if H is None:
                raise ValueError("Could not align the images. Try images with clearer overlapping areas.")

            result = self._warp_images(img2, img1, H)

            success = cv2.imwrite(output_path, result)
            if not success:
                raise ValueError(f"Could not save the stitched image to {output_path}. Check if the folder exists and you have permission.")

        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

def run_cli():
    parser = argparse.ArgumentParser(
        description="Stitch two images into one. Example: python image_stitcher.py first.png second.png output.png"
    )
    parser.add_argument("--gui", action="store_true", help="Launch the graphical interface instead")
    parser.add_argument("image1", nargs="?", help="Path to the first image (e.g., first.png)")
    parser.add_argument("image2", nargs="?", help="Path to the second image (e.g., second.png)")
    parser.add_argument("output", nargs="?", help="Path to save the stitched image (e.g., output.png)")

    args = parser.parse_args()

    if args.gui:
        run_gui()
        return

    if not args.image1 or not args.image2 or not args.output:
        parser.error("the following arguments are required: image1, image2, output (unless --gui is used)")

    print("Starting image stitching...")
    try:
        plugin = ImageStitcherPlugin()
        plugin.stitch(args.image1, args.image2, args.output)
        print(f"Success! Stitched image saved to {args.output}")
    except Exception as e:
        print(f"Oops, something went wrong: {str(e)}")
        print("Tips: Make sure the images exist, have overlapping parts, and the output path is valid.")

def run_gui():
    root = tk.Tk()
    root.title("Image Stitcher")
    root.geometry("400x300")

    def select_file(entry):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def save_file(entry):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def stitch_images():
        image1_path = entry1.get()
        image2_path = entry2.get()
        output_path = entry3.get()

        if not (image1_path and image2_path and output_path):
            messagebox.showerror("Error", "Please select both input images and an output path.")
            return

        try:
            plugin = ImageStitcherPlugin()
            plugin.stitch(image1_path, image2_path, output_path)
            messagebox.showinfo("Success", f"Stitched image saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stitch images: {str(e)}\n\nTips: Ensure images have overlapping areas and the output path is valid.")

    tk.Label(root, text="Image Stitcher", font=("Arial", 16)).pack(pady=10)

    frame1 = tk.Frame(root)
    frame1.pack(pady=5)
    tk.Label(frame1, text="First Image        :").pack(side=tk.LEFT)
    entry1 = tk.Entry(frame1, width=30)
    entry1.pack(side=tk.LEFT, padx=5)
    tk.Button(frame1, text="Browse", command=lambda: select_file(entry1)).pack(side=tk.LEFT)

    frame2 = tk.Frame(root)
    frame2.pack(pady=5)
    tk.Label(frame2, text="Second Image  :").pack(side=tk.LEFT)
    entry2 = tk.Entry(frame2, width=30)
    entry2.pack(side=tk.LEFT, padx=5)
    tk.Button(frame2, text="Browse", command=lambda: select_file(entry2)).pack(side=tk.LEFT)

    frame3 = tk.Frame(root)
    frame3.pack(pady=5)
    tk.Label(frame3, text="Output Image  :").pack(side=tk.LEFT)
    entry3 = tk.Entry(frame3, width=30)
    entry3.pack(side=tk.LEFT, padx=5)
    tk.Button(frame3, text="Browse", command=lambda: save_file(entry3)).pack(side=tk.LEFT)

    tk.Button(root, text="Stitch Images", command=stitch_images, bg="green", fg="white", font=("Arial", 12)).pack(pady=20)
    tk.Button(root, text="Exit", command=root.quit, bg="red", fg="white", font=("Arial", 12)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_cli()