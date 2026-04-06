# DUAL-Pose: Efficient Dual-Branch Graph Networks for Skeleton-Based Yoga Pose Recognition

**Accepted at CVPR Workshops 2026**

> Rashi Niyas P, Hitika Tiwari, Tushar Shinde  
> IIT Madras Zanzibar  
> `{zda24m005, hitika, shinde}@iitmz.ac.in`

---

## Overview

DUAL-Pose is a lightweight (~51K parameters), privacy-preserving skeleton-only framework for yoga pose recognition.  
It combines:

| Branch | Input | Role |
|--------|-------|------|
| **GCN branch** | 33 joints × 3 coords | Local anatomical topology |
| **MLP branch** | 113-D geometric features | Global bone angles & joint relations |

Both branches process **16 synthetic yaw-rotated views** of each pose, aggregated via learned attention weights.

## Results

| Dataset  | Top-1 Acc | Parameters |
|----------|-----------|------------|
| Yoga-82  | 88.62%    | ~51K       |
| Yoga-16  | 97.25%    | ~51K       |

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


@InProceedings{Verma2020Yoga82,
  author    = {Radhi Niyas P., H. Tiwari, and Tushar Shinde},
  title     = {Dual-branch Unified Aggregation for Latent Pose Representation},
  booktitle = {IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshop},
  year      = {2026},
}


```

## License
MIT
