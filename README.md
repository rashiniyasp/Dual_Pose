# DUAL-Pose: Efficient Dual-Branch Graph Networks for Skeleton-Based Yoga Pose Recognition

**Accepted at CVPR Workshops 2026**
[CVPRw Paper Link](https://openaccess.thecvf.com/content/CVPR2026W/SAUAFG/html/P_DUAL-Pose_Efficient_Dual-Branch_Graph_Networks_for_Skeleton-Based_Yoga_Pose_Recognition_CVPRW_2026_paper.html) [Website](https://rashiniyasp.github.io/Dual_Pose/)

🌐 **[Try the Live Web Demo!](https://rashiniyasp.github.io/Dual_Pose/static/index.html)**  
Experience DUAL-Pose in real-time right in your browser. This 100% client-side web application preserves privacy by processing everything locally without sending video data to any server.

---

## Overview

DUAL-Pose is a lightweight (~51K parameters), privacy-preserving skeleton-only framework for yoga pose recognition.  
It combines:

| Branch | Input | Role |
|--------|-------|------|
| **GCN branch** | 33 joints × 3 coords | Local anatomical topology |
| **MLP branch** | 113-D geometric features | Global bone angles & joint relations |

Both branches process **16 synthetic yaw-rotated views** of each pose, aggregated via learned attention weights.
<img width="997" height="1526" alt="image" src="https://github.com/user-attachments/assets/3b616f97-dd1a-4c3c-9a17-2ac3eec908d2" />


## Results

| Dataset  | Top-1 Acc | Parameters | GFLOPs  | Inference Latency |
|----------|-----------|------------|---------|-------------------|
| Yoga-82  | 88.62%    | 51,891     | 5.50 M  | 1.66 ms / sample  |
| Yoga-16  | 97.25%    | 47,601     | 5.49 M  | 0.79 ms / sample  |

## 🌐 Live Web Demo

DUAL-Pose includes a privacy-preserving, 100% client-side web application for live yoga pose classification! 
It runs the DUAL-Pose model directly in your browser using ONNX Web Runtime— Only the extracted skeleton is rendered on a clean white canvas.

## Repository Structure

```
DUAL-Pose/
├── configs/config.py         # All hyperparameters
├── data/
│   ├── preprocessing.py      # Step 1: Images → .npy via BlazePose
│   └── dataset.py            # Step 2: DualPoseDataset loader
├── models/
│   ├── gcn_layers.py         # GCNLayer + BlazePose adjacency matrix
│   └── dual_pose.py          # Full DUAL-Pose model
├── utils/
│   ├── training.py           # EarlyStopping, fit(), plot_history()
│   └── evaluation.py         # test(), confusion matrix
├── train.py                  # CLI training script
└── test.py                   # CLI evaluation script
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Skeleton Data
Pre-extracted BlazePose `.npy` files are available on Kaggle:  
📦 [Yoga-82 Keypoints 2026](https://www.kaggle.com/datasets/rashiniyasp/yoga-82-keypoints-2026/data)
 
📦 [Yoga-16 Keypoints 2026](https://www.kaggle.com/datasets/rashiniyasp/yoga-16-keypoint-dataset)


Place data under:
```
skeletons/
  yoga82/
    train/  class_name/ *.npy
    test/   class_name/ *.npy
    labels.txt
```

### 3. (Optional) Extract keypoints from raw images yourself
```bash
python -m data.preprocessing --images_root ./raw_images/yoga82 --output_root ./skeletons/yoga82
```

### 4. Train
```bash
python train.py --dataset yoga82   # or yoga16
```

### 5. Evaluate
```bash
python test.py --dataset yoga82
```

## Citation

If you use this code or data, please cite:

```bibtex


@InProceedings{P_2026_CVPR,
    author    = {P, Rashi Niyas and Tiwari, Hitika and Shinde, Tushar},
    title     = {DUAL-Pose: Efficient Dual-Branch Graph Networks for Skeleton-Based Yoga Pose Recognition},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops},
    month     = {June},
    year      = {2026},
    pages     = {8884-8893}
}

```

## License
MIT
