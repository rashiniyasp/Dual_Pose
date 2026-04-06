"""
Step 1 – Extract BlazePose keypoints from raw images and save as .npy files.

Usage:
    python -m data.preprocessing \
        --images_root ./raw_images/yoga82 \
        --output_root ./skeletons/yoga82

Expected input folder layout:
    images_root/
        class_name_1/
            img001.jpg
            img002.jpg
        class_name_2/
            ...

Output layout mirrors the input:
    output_root/
        class_name_1/
            img001.npy   # shape (33, 4) — x, y, z, visibility
        ...
    output_root/labels.txt  # class names sorted
"""

import os
import argparse
import numpy as np
import cv2
import mediapipe as mp
from tqdm import tqdm


def extract_keypoints(image_path: str, pose) -> np.ndarray | None:
    """Run BlazePose on one image; return (33, 4) array or None on failure."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result  = pose.process(img_rgb)
    if not result.pose_landmarks:
        return None
    lm = result.pose_landmarks.landmark
    return np.array([[l.x, l.y, l.z, l.visibility] for l in lm], dtype=np.float32)


def run(images_root: str, output_root: str) -> None:
    mp_pose = mp.solutions.pose
    pose    = mp_pose.Pose(static_image_mode=True,
                           model_complexity=2,
                           min_detection_confidence=0.5)

    class_names = sorted([d for d in os.listdir(images_root)
                          if os.path.isdir(os.path.join(images_root, d))])
    os.makedirs(output_root, exist_ok=True)

    # Save label mapping
    with open(os.path.join(output_root, "labels.txt"), "w") as f:
        f.write("\n".join(class_names))

    skipped = 0
    for cls in tqdm(class_names, desc="Classes"):
        in_dir  = os.path.join(images_root, cls)
        out_dir = os.path.join(output_root, cls)
        os.makedirs(out_dir, exist_ok=True)

        for fname in os.listdir(in_dir):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            kp = extract_keypoints(os.path.join(in_dir, fname), pose)
            if kp is None:
                skipped += 1
                continue
            np.save(os.path.join(out_dir, os.path.splitext(fname)[0] + ".npy"), kp)

    pose.close()
    print(f"Done. Skipped {skipped} images (no pose detected).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_root", required=True)
    parser.add_argument("--output_root", required=True)
    args = parser.parse_args()
    run(args.images_root, args.output_root)
