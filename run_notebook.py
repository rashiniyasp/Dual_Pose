import os
import numpy as np
import torch
import math
from torch.utils.data import Dataset, DataLoader
from collections import Counter
import mediapipe as mp 

# CONFIGURATION
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Update this to your actual output path from the previous step
SKELETON_DATA_ROOT = '../Yoga 82 keypoints/Yoga_82_Balanced_2026' 

# ==========================================
# 1. FEATURE RE-CALCULATION HELPER
# ==========================================


def get_pose_features_dynamic(landmarks_xyz):
    """
    Input: (33, 3) array of coordinates
    Output: Combined feature vector [Coords + Angles + Bones] (No visibility yet)
    """
    # 1. Flatten Coords (99)
    coords = landmarks_xyz.flatten()
    
    # 2. Angles (8) - Vectorized
    # Hardcoded landmark indices for:
    # 0: RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST
    # 1: RIGHT_HIP, RIGHT_SHOULDER, RIGHT_ELBOW
    # 2: LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST
    # 3: LEFT_HIP, LEFT_SHOULDER, LEFT_ELBOW
    # 4: RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE
    # 5: RIGHT_SHOULDER, RIGHT_HIP, RIGHT_KNEE
    # 6: LEFT_HIP, LEFT_KNEE, LEFT_ANKLE
    # 7: LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE
    idx_b = np.array([14, 12, 13, 11, 26, 24, 25, 23])
    idx_a = np.array([12, 24, 11, 23, 24, 12, 23, 11])
    idx_c = np.array([16, 14, 15, 13, 28, 26, 27, 25])
    
    ba = landmarks_xyz[idx_a] - landmarks_xyz[idx_b]
    bc = landmarks_xyz[idx_c] - landmarks_xyz[idx_b]
    
    norm_ba = np.linalg.norm(ba, axis=1)
    norm_bc = np.linalg.norm(bc, axis=1)
    
    # Avoid division by zero
    valid = (norm_ba > 1e-6) & (norm_bc > 1e-6)
    
    angles = np.zeros(8)
    if np.any(valid):
        cosine_angle = np.sum(ba[valid] * bc[valid], axis=1) / (norm_ba[valid] * norm_bc[valid])
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angles[valid] = np.degrees(np.arccos(cosine_angle)) / 180.0
        
    # 3. Bones/Vectors (35*3 = 105) - Vectorized
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
        (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
        (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
        (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (27, 29), (27, 31),
        (29, 31), (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
    ]
    start_idx = [c[0] for c in connections]
    end_idx = [c[1] for c in connections]
    
    vectors = (landmarks_xyz[end_idx] - landmarks_xyz[start_idx]).flatten()
    
    return np.concatenate([coords, angles, vectors])

# ==========================================
# 2. DATASET CLASS WITH VISIBILITY TOGGLE
# ==========================================

class MultiViewYogaDataset(Dataset):
    def __init__(self, root_dir, split='train', transform=False, use_visibility=True):
        self.data_dir = os.path.join(root_dir, split)
        self.files = []
        self.labels = []
        self.transform = transform      # Apply Augmentation (Noise/Scale)
        self.use_visibility = use_visibility # Type 1 (True) or Type 2 (False)
        
        # Load file list
        self.classes = sorted([d for d in os.listdir(self.data_dir) 
                               if os.path.isdir(os.path.join(self.data_dir, d))])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        self.label_counts = Counter()
        
        print(f"Loading {split} | Augment={transform} | Visibility={use_visibility}")
        
        for cls_name in self.classes:
            cls_path = os.path.join(self.data_dir, cls_name)
            if not os.path.exists(cls_path): continue
                
            idx = self.class_to_idx[cls_name]
            for f in os.listdir(cls_path):
                if f.endswith('.npy'):
                    self.files.append(os.path.join(cls_path, f))
                    self.labels.append(idx)
                    self.label_counts[idx] += 1

    def __len__(self):
        return len(self.files)

    def augment_skeleton(self, skeleton_xyz):
        # Scale
        scale = np.random.uniform(0.9, 1.1)
        skeleton_xyz = skeleton_xyz * scale
        # Noise
        noise = np.random.normal(0, 0.02, skeleton_xyz.shape)
        skeleton_xyz = skeleton_xyz + noise
        return skeleton_xyz

    def generate_views(self, skeleton_xyz, visibility_arr):
        views = []
        # Generate 16 angles from -180 to 180 (Full rotation coverage)
        angles_deg = np.linspace(-180, 180, 16)
        
        for deg in angles_deg:
            theta = np.deg2rad(deg)
            c, s = np.cos(theta), np.sin(theta)
            # Rotation around Y axis
            rot_mat = np.array([
                [c,  0, s],
                [0,  1, 0],
                [-s, 0, c]
            ])
            
            # Rotate coordinates
            rotated_xyz = np.dot(skeleton_xyz, rot_mat)
            
            # Recalculate features (Coords + Angles + Bones) -> Size 212
            feats = get_pose_features_dynamic(rotated_xyz)
            
            # Handling Type 1 vs Type 2
            if self.use_visibility:
                # Type 1: Append Visibility (212 + 33 = 245)
                feats = np.concatenate([feats, visibility_arr])
            
            views.append(feats)
            
        return np.array(views, dtype=np.float32)

    def __getitem__(self, idx):
        # 1. Load Raw Data
        raw_data = np.load(self.files[idx])
        
        # 2. Extract Components
        # Handle both raw (33, 4) and preprocessed (245,) formats
        if raw_data.shape == (33, 4):
            coords = raw_data[:, :3] # Shape (33, 3)
            visibility = raw_data[:, 3] # Shape (33,)
        else:
            raw_data = raw_data.flatten()
            coords = raw_data[:99].reshape(33, 3)
            visibility = raw_data[-33:]
        
        # 3. Augment (Training only)
        if self.transform:
            coords = self.augment_skeleton(coords)
            
        # 4. Generate Views
        # Returns shape (16, Feature_Dim)
        multi_view_feats = self.generate_views(coords, visibility)
        
        return torch.FloatTensor(multi_view_feats), torch.tensor(self.labels[idx], dtype=torch.long)



# ==========================================
# 3. SETUP LOADERS & CHECK DIMENSIONS
# ==========================================

# --- CONFIG A: TYPE 1 (WITH VISIBILITY) ---
print("\n--- CHECKING TYPE 1 (WITH VISIBILITY) ---")
train_ds_vis = MultiViewYogaDataset(SKELETON_DATA_ROOT, 'train', transform=True, use_visibility=True)
loader_vis = DataLoader(train_ds_vis, batch_size=256, shuffle=True)

# Check one batch
data, label = next(iter(loader_vis))
print(f"Batch Shape: {data.shape}") 
# Expected: [Batch_Size, 16_Views, 245_Features]
# 245 = 99(Coords) + 8(Angles) + 105(Bones) + 33(Vis)

if data.shape[-1] == 245:
    print("[SUCCESS] Type 1 Dimension Check Passed: 245 features")
else:
    print(f"[ERROR] Type 1 Dimension Mismatch: Got {data.shape[-1]}, expected 245")


# --- CONFIG B: TYPE 2 (WITHOUT VISIBILITY) ---
print("\n--- CHECKING TYPE 2 (WITHOUT VISIBILITY) ---")
train_ds_no_vis = MultiViewYogaDataset(SKELETON_DATA_ROOT, 'train', transform=True, use_visibility=False)
loader_no_vis = DataLoader(train_ds_no_vis, batch_size=256, shuffle=True)

# Check one batch
data, label = next(iter(loader_no_vis))
print(f"Batch Shape: {data.shape}")
# Expected: [Batch_Size, 16_Views, 212_Features]
# 212 = 99(Coords) + 8(Angles) + 105(Bones)

if data.shape[-1] == 212:
    print("[SUCCESS] Type 2 Dimension Check Passed: 212 features")
else:
    print(f"[ERROR] Type 2 Dimension Mismatch: Got {data.shape[-1]}, expected 212")

# ==========================================
# 4. FINAL PRODUCTION LOADERS (Select Type Here)
# ==========================================
# Change USE_VISIBILITY_FINAL to True or False depending on which model you are training
USE_VISIBILITY_FINAL = False

print(f"\nInitializing Final Loaders (Visibility={USE_VISIBILITY_FINAL})...")

train_ds = MultiViewYogaDataset(SKELETON_DATA_ROOT, 'train', transform=True, use_visibility=USE_VISIBILITY_FINAL)
valid_ds = MultiViewYogaDataset(SKELETON_DATA_ROOT, 'validation', transform=False, use_visibility=USE_VISIBILITY_FINAL)
test_ds = MultiViewYogaDataset(SKELETON_DATA_ROOT, 'test', transform=False, use_visibility=USE_VISIBILITY_FINAL)

train_loader = DataLoader(train_ds, batch_size=256, shuffle=True, num_workers=0)
valid_loader = DataLoader(valid_ds, batch_size=256, shuffle=False, num_workers=0)
test_loader = DataLoader(test_ds, batch_size=256, shuffle=False, num_workers=0)

# Calculate Class Weights for Loss Function
counts = [train_ds.label_counts[i] for i in range(len(train_ds.classes))]
# Avoid division by zero if a class is empty (unlikely but safe)
counts = [c if c > 0 else 1 for c in counts] 
weights = sum(counts) / (len(counts) * torch.FloatTensor(counts))
weights = weights.to(DEVICE)
print(f"train length:{len(train_ds)}")
print(f"valid length:{len(valid_ds)}")
print(f"test length:{len(test_ds)}")

print("Loaders Ready.")

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
# from torchdiffeq import odeint
import matplotlib.pyplot as plt
from tqdm import tqdm
import math
import copy
import torch.optim as optim


# 1. The Dynamics Function (The "Brain" of the ODE)
class ODEFunc(nn.Module):
    def __init__(self, dim, hidden_dim):
        super(ODEFunc, self).__init__()
        # WIDE internal network (Bottleneck style for efficiency)
        self.net = nn.Sequential(
            nn.Linear(dim, hidden_dim),
            nn.Softplus(), # Softplus is smoother than ReLU, better for ODEs
            nn.Linear(hidden_dim, hidden_dim),
            nn.Softplus(),
            nn.Linear(hidden_dim, dim)
        )

    def forward(self, t, x):
        return self.net(x)

import torch
import torch.nn as nn
import torch.nn.functional as F
import mediapipe as mp 

class GCNLayer(nn.Module):
    """
    Very small, dependency-free GCN layer:
    X' = A_hat @ X @ W + b
    where A_hat is precomputed normalized adjacency with self-loops.
    """
    def __init__(self, in_feats, out_feats, bias=True):
        super().__init__()
        self.linear = nn.Linear(in_feats, out_feats, bias=bias)

    def forward(self, x, A_hat):
        # x: (B, N, in_feats)
        # A_hat: (N, N)
        # Aggregate neighbors
        x = torch.einsum('ij,bjk->bik', A_hat, x)   # (B,N,in_feats)
        x = self.linear(x)                          # (B,N,out_feats)
        return x

def build_adjacency_matrix(num_nodes=33):
    # Build adjacency from mediapipe connections (hardcoded)
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
        (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
        (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
        (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (27, 29), (27, 31),
        (29, 31), (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
    ]
    A = torch.zeros((num_nodes, num_nodes), dtype=torch.float32)
    for a, b in connections:
        if a < num_nodes and b < num_nodes:
            A[a, b] = 1.0
            A[b, a] = 1.0
    # add self-loops
    for i in range(num_nodes):
        A[i, i] = 1.0
    # Symmetric normalization: D^{-1} A
    deg = A.sum(dim=1)            # (N,)
    deg_inv = torch.where(deg > 0, 1.0 / deg, torch.zeros_like(deg))
    D_inv = torch.diag(deg_inv)
    A_hat = D_inv @ A
    return A_hat  # (N,N)

class GCN_Attn_NodeODE(nn.Module):
    """
    Pipeline:
      per-frame GCN encoder (coords -> node embeddings) + small global-MLP (angles+vectors)
      -> per-frame embeddings
      -> Attention pooling across 16 frames (learned scalar attention)
      -> Neural ODE applied to that single pooled vector
      -> Classifier MLP
    """
    def __init__(self,
                 input_dim=212,       # unchanged (frame feature dim)
                 num_nodes=33,
                 node_in_dim=3,
                 gcn_hidden=96,       # tuned to meet ~75k params
                 global_feat_dim=113, # input_dim - 99 coords = 113
                 global_hidden=64,
                 latent_dim=80,       # pooled embedding dimension (see tuning)
                 ode_hidden_dim=64,
                 clf_hidden=192,
                 num_classes=82):
        super().__init__()

        # Precompute adjacency (register as buffer so it moves with model)
        A_hat = build_adjacency_matrix(num_nodes=num_nodes)
        self.register_buffer('A_hat', A_hat)   # (33,33)

        # GCN encoder (two small GCN layers)
        self.gcn1 = GCNLayer(node_in_dim, gcn_hidden)
        self.gcn2 = GCNLayer(gcn_hidden, gcn_hidden)
        self.gcn_ln = nn.LayerNorm(gcn_hidden)

        # Global MLP for remaining per-frame features (angles + bone-vectors)
        self.global_mlp = nn.Sequential(
            nn.Linear(global_feat_dim, global_hidden),
            nn.ReLU(),
            nn.LayerNorm(global_hidden)
        )

        # Final per-frame projection to latent_dim
        self.readout = nn.Sequential(
            nn.Linear(gcn_hidden + global_hidden, latent_dim),
            nn.ReLU(),
            nn.LayerNorm(latent_dim)
        )

        # Attention pooling parameters (learned query)
        self.attn_query = nn.Linear(latent_dim, 1)  # produces scalar score per frame

        # Neural ODE block
        self.ode_func = ODEFunc(latent_dim, ode_hidden_dim)  # re-uses your ODEFunc definition
        self.integration_time = torch.tensor([0.0, 1.0]).float()

        # Classifier MLP
        self.classifier = nn.Sequential(
            nn.Linear(latent_dim, clf_hidden),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(clf_hidden, num_classes)
        )

    def forward(self, x):
        # x: [B, 16, 212]
        batch_size, num_views, feat_dim = x.shape
        assert num_views == 16, "Expected 16 views"

        # Flatten all frames for per-frame processing
        x_flat = x.view(-1, feat_dim)   # [B*16, 212]

        # Split coordinates and global features
        coords = x_flat[:, :99].view(-1, 33, 3)   # [B*16, 33, 3]
        global_feats = x_flat[:, 99:]             # [B*16, 113]

        # Move A_hat to same device (buffer already registered)
        A_hat = self.A_hat
        if x_flat.is_cuda and not A_hat.is_cuda:
            A_hat = A_hat.to(x_flat.device)

        # --- GCN node processing ---
        h = F.relu(self.gcn1(coords, A_hat))      # [B*16, 33, gcn_hidden]
        h = F.relu(self.gcn2(h, A_hat))           # [B*16, 33, gcn_hidden]
        # Pool nodes to get per-frame spatial embedding (mean)
        node_pool = h.mean(dim=1)                 # [B*16, gcn_hidden]
        node_pool = self.gcn_ln(node_pool)

        # --- Global feature branch ---
        g = self.global_mlp(global_feats)         # [B*16, global_hidden]

        # --- Per-frame embedding ---
        per_frame = torch.cat([node_pool, g], dim=1)   # [B*16, gcn_hidden+global_hidden]
        per_frame = self.readout(per_frame)            # [B*16, latent_dim]

        # Reshape back to [B, 16, latent_dim]
        per_frame_seq = per_frame.view(batch_size, num_views, -1)  # [B,16,latent_dim]

        # --- Attention pooling across frames (pre-ODE) ---
        # scalar scores
        scores = self.attn_query(per_frame_seq).squeeze(-1)  # [B,16]
        attn_weights = torch.softmax(scores, dim=1).unsqueeze(-1)  # [B,16,1]
        z0 = torch.sum(attn_weights * per_frame_seq, dim=1)  # [B, latent_dim]

        # --- Neural ODE applied to the single pooled z0 ---
        if z0.is_cuda: self.integration_time = self.integration_time.cuda()
#         zT = odeint(self.ode_func, z0, self.integration_time, method='dopri5', rtol=1e-3, atol=1e-3)[1]

        # --- Classify ---
        logits = self.classifier(zT)  # [B, num_classes]
        return logits

# === Instantiate the model and print parameter count (same pattern as original file) ===
model = GCN_Attn_NodeODE(
    input_dim=212,
    num_nodes=33,
    node_in_dim=3,
    gcn_hidden=96,
    global_feat_dim=113,
    global_hidden=64,
    latent_dim=80,
    ode_hidden_dim=64,
    clf_hidden=192,
    num_classes=82
).to(DEVICE)

params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Modified GCN-Attn-NODE Model Parameters: {params:,}")

class EarlyStopping:
    def __init__(self, patience=7, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0

def plot_history(history):
    acc = history['train_acc']
    val_acc = history['val_acc']
    loss = history['train_loss']
    val_loss = history['val_loss']
    epochs_range = range(len(acc))

    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.show()


# --- TRAINING SETUP ---
# Label Smoothing helps with noisy skeletons
criterion = nn.CrossEntropyLoss( weight=weights,label_smoothing=0.2)

# Weight Decay is CRITICAL for Transformers to prevent overfitting
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-3)

EPOCHS = 100 # Adjusted for typical convergence
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

early_stopper = EarlyStopping(patience=10,min_delta=0.005)
history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ==========================================
# TEST EVALUATION CODE
# ==========================================

def evaluate_model(model, loader, device, model_path=None):
    # 1. Load the saved weights (Best Practice)
    if model_path:
        print(f"Loading weights from {model_path}...")
        try:
            model.load_state_dict(torch.load(model_path, map_location=device))
        except Exception as e:
            print(f"Warning: Could not load weights from disk ({e}). Using model in memory.")
    
    model.eval()
    all_preds = []
    all_labels = []
    
    print("Running evaluation on Test Set...")
    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            # Forward pass
            outputs = model(inputs)
            
            # Get predictions
            _, predicted = torch.max(outputs.data, 1)
            
            # Move to CPU and store
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # 2. Calculate Metrics
    accuracy = accuracy_score(all_labels, all_preds)
    print(f"\n[SUCCESS] Final Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # 3. Detailed Classification Report
    # Get class names from dataset
    class_names = loader.dataset.classes
    
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    print(classification_report(all_labels, all_preds, target_names=class_names, digits=4))
    
    return all_labels, all_preds, class_names

def plot_confusion_matrix(y_true, y_pred, classes):
    cm = confusion_matrix(y_true, y_pred)
    
    # Normalize matrix to show percentages (easier to read with 82 classes)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    plt.figure(figsize=(24, 20)) # Large figure for 82 classes
    sns.heatmap(
        cm_norm, 
        annot=False, # Too messy with 82 classes, set True if you want numbers
        fmt='.2f', 
        cmap='Blues', 
        xticklabels=classes, 
        yticklabels=classes
    )
    plt.title('Normalized Confusion Matrix (Test Set)')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.show()

import torch
import torch.nn as nn
import torch.nn.functional as F

# ---- GCN Layer ----
class GCNLayer(nn.Module):
    def __init__(self, in_feats, out_feats):
        super().__init__()
        self.linear = nn.Linear(in_feats, out_feats)

    def forward(self, x, A_hat):
        x = torch.einsum('ij,bjk->bik', A_hat, x)
        return self.linear(x)


def build_adjacency_matrix(num_nodes=33):
    # Hardcoded POSE_CONNECTIONS
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
        (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
        (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
        (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (27, 29), (27, 31),
        (29, 31), (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
    ]

    A = torch.zeros(num_nodes, num_nodes)
    for i, j in connections:
        if i < num_nodes and j < num_nodes:
            A[i, j] = 1
            A[j, i] = 1
    A += torch.eye(num_nodes)

    deg = A.sum(dim=1)
    A_hat = torch.diag(1.0 / deg) @ A
    return A_hat


class GCN_Attention_MLP(nn.Module):
    def __init__(self,
                 input_dim=212,
                 num_nodes=33,
                 gcn_hidden=128,
                 global_feat_dim=113,
                 global_hidden=64,
                 latent_dim=128,
                 clf_hidden=128,
                 num_classes=82):
        super().__init__()

        A_hat = build_adjacency_matrix(num_nodes)
        self.register_buffer('A_hat', A_hat)

        # GCN encoder
        self.gcn1 = GCNLayer(3, gcn_hidden)
        self.gcn2 = GCNLayer(gcn_hidden, gcn_hidden)
        self.node_ln = nn.LayerNorm(gcn_hidden)

        # Global features
        self.global_mlp = nn.Sequential(
            nn.Linear(global_feat_dim, global_hidden),
            nn.ReLU(),
            nn.LayerNorm(global_hidden)
        )

        # Frame embedding
        self.readout = nn.Sequential(
            nn.Linear(gcn_hidden + global_hidden, latent_dim),
            nn.ReLU(),
            nn.LayerNorm(latent_dim)
        )

        # Attention pooling
        self.attn = nn.Linear(latent_dim, 1)

        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(latent_dim, clf_hidden),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(clf_hidden, num_classes)
        )

    def forward(self, x):
        # x: [B,16,212]
        B, T, D = x.shape
        x = x.view(B * T, D)

        coords = x[:, :99].view(B * T, 33, 3)
        global_feats = x[:, 99:]

        A_hat = self.A_hat.to(x.device)

        h = F.relu(self.gcn1(coords, A_hat))
        h = F.relu(self.gcn2(h, A_hat))
        h = h.mean(dim=1)
        h = self.node_ln(h)

        g = self.global_mlp(global_feats)

        frame_emb = self.readout(torch.cat([h, g], dim=1))
        frame_emb = frame_emb.view(B, T, -1)

        # Attention pooling
        scores = self.attn(frame_emb).squeeze(-1)
        weights = torch.softmax(scores, dim=1).unsqueeze(-1)
        pooled = torch.sum(weights * frame_emb, dim=1)

        return self.classifier(pooled)

model = GCN_Attention_MLP(
    input_dim=212,
    num_nodes=33,
    gcn_hidden=96,
    global_feat_dim=113,
    global_hidden=64,
    latent_dim=128,
    clf_hidden=64,
    num_classes=82
).to(DEVICE)

params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Method 3 (GCN + Attention) params: {params:,}")



# --- TRAINING SETUP ---
# Label Smoothing helps with noisy skeletons
criterion = nn.CrossEntropyLoss( weight=weights,label_smoothing=0.2)

# Weight Decay is CRITICAL for Transformers to prevent overfitting
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-3)

EPOCHS = 100 # Adjusted for typical convergence
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

early_stopper = EarlyStopping(patience=10,min_delta=0.005)
history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

print(f"\nStarting Training (Device: {DEVICE})...")

print("Skipping Yoga 82 Training as weights are already saved.")
for epoch in range(0):
    # --- TRAIN ---
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    loop = tqdm(train_loader, desc=f"Ep {epoch+1}/{EPOCHS}", leave=False)
    
    for inputs, labels in loop:
        inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
        
        # Explicit Noise Augmentation on Features (Optional but helpful)
        noise = torch.randn_like(inputs) * 0.01
        inputs = inputs + noise
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        loss.backward()
        # Clip gradients for stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        loop.set_postfix(loss=loss.item())
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = correct / total
    
    # --- VALIDATION ---
    model.eval()
    val_loss = 0.0
    val_correct = 0
    val_total = 0
    
    with torch.no_grad():
        for inputs, labels in valid_loader: # Using Valid Loader (Not Test)
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            val_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()
            
    val_epoch_loss = val_loss / len(valid_loader)
    val_epoch_acc = val_correct / val_total
    
    # --- SCHEDULER & HISTORY ---
    scheduler.step()
    
    history['train_loss'].append(epoch_loss)
    history['train_acc'].append(epoch_acc)
    history['val_loss'].append(val_epoch_loss)
    history['val_acc'].append(val_epoch_acc)
    
    print(f"Epoch {epoch+1} | Train Acc: {epoch_acc:.4f} | Val Acc: {val_epoch_acc:.4f} | LR: {scheduler.get_last_lr()[0]:.6f}")
    
    # --- EARLY STOPPING ---
    early_stopper(val_epoch_loss)
    if early_stopper.early_stop:
        print("Early stopping triggered!")
        break

# --- SAVE & PLOT ---
# torch.save(model.state_dict(), 'NoNODE_50k.pth')
print("Model already Saved.")
# plot_history(history)



# ==========================================
# RUN EVALUATION
# ==========================================

# Run test using the model instance 'model' and 'test_loader' defined previously
y_true, y_pred, classes = evaluate_model(
    model, 
    test_loader, 
    DEVICE, 
    model_path='NoNODE_50k.pth'
)

# Plot it
plot_confusion_matrix(y_true, y_pred, classes)

import time
from thop import profile

# Measure FLOPs
dummy_input = torch.randn(1, 16, 212).to(DEVICE)
flops, params = profile(model, inputs=(dummy_input, ), verbose=False)
print(f"Yoga 82 Model - FLOPs: {flops/1e6:.2f} M, Params: {params:,}")

# Measure Latency
model.eval()
with torch.no_grad():
    # Warmup
    for _ in range(10): model(dummy_input)
    
    start_time = time.time()
    for _ in range(100):
        model(dummy_input)
    end_time = time.time()
    
latency = (end_time - start_time) / 100.0 * 1000 # in ms
print(f"Yoga 82 Model - Inference Latency: {latency:.2f} ms / sample")

SKELETON_DATA_ROOT_16 = "../Yoga 16 keypoints"
print("Initializing Loaders for Yoga 16...")
train_ds_16 = MultiViewYogaDataset(SKELETON_DATA_ROOT_16, 'train', transform=True, use_visibility=False)
valid_ds_16 = MultiViewYogaDataset(SKELETON_DATA_ROOT_16, 'valid', transform=False, use_visibility=False)
test_ds_16 = MultiViewYogaDataset(SKELETON_DATA_ROOT_16, 'test', transform=False, use_visibility=False)

train_loader_16 = DataLoader(train_ds_16, batch_size=256, shuffle=True, num_workers=0)
valid_loader_16 = DataLoader(valid_ds_16, batch_size=256, shuffle=False, num_workers=0)
test_loader_16 = DataLoader(test_ds_16, batch_size=256, shuffle=False, num_workers=0)

model_16 = GCN_Attention_MLP(
    input_dim=212,
    num_nodes=33,
    gcn_hidden=96,
    global_feat_dim=113,
    global_hidden=64,
    latent_dim=128,
    clf_hidden=64,
    num_classes=16 # 16 Classes
).to(DEVICE)

criterion_16 = nn.CrossEntropyLoss(label_smoothing=0.2)
optimizer_16 = torch.optim.AdamW(model_16.parameters(), lr=0.001, weight_decay=1e-3)
scheduler_16 = optim.lr_scheduler.CosineAnnealingLR(optimizer_16, T_max=EPOCHS)
early_stopper_16 = EarlyStopping(patience=10, min_delta=0.005)
history_16 = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

print("\nStarting Training for Yoga 16...")
for epoch in range(EPOCHS):
    model_16.train()
    running_loss, correct, total = 0.0, 0, 0
    
    for inputs, labels in train_loader_16:
        inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
        inputs = inputs + torch.randn_like(inputs) * 0.01
        
        optimizer_16.zero_grad()
        outputs = model_16(inputs)
        loss = criterion_16(outputs, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model_16.parameters(), 1.0)
        optimizer_16.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
    epoch_loss = running_loss / len(train_loader_16)
    epoch_acc = correct / total
    
    model_16.eval()
    val_loss, val_correct, val_total = 0.0, 0, 0
    with torch.no_grad():
        for inputs, labels in valid_loader_16:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            outputs = model_16(inputs)
            loss = criterion_16(outputs, labels)
            val_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()
            
    val_epoch_loss = val_loss / len(valid_loader_16)
    val_epoch_acc = val_correct / val_total
    
    scheduler_16.step()
    history_16['train_loss'].append(epoch_loss)
    history_16['train_acc'].append(epoch_acc)
    history_16['val_loss'].append(val_epoch_loss)
    history_16['val_acc'].append(val_epoch_acc)
    
    print(f"Epoch {epoch+1} | Train Acc: {epoch_acc:.4f} | Val Acc: {val_epoch_acc:.4f}")
    
    early_stopper_16(val_epoch_loss)
    if early_stopper_16.early_stop:
        print("Early stopping triggered for Yoga 16!")
        break

torch.save(model_16.state_dict(), 'Yoga16_Weights.pth')
print("Yoga 16 Model Saved.")

# Evaluate FLOPs and Latency for Yoga 16 model
flops_16, params_16 = profile(model_16, inputs=(dummy_input, ), verbose=False)
print(f"Yoga 16 Model - FLOPs: {flops_16/1e6:.2f} M, Params: {params_16:,}")

model_16.eval()
with torch.no_grad():
    for _ in range(10): model_16(dummy_input)
    start_time = time.time()
    for _ in range(100): model_16(dummy_input)
    end_time = time.time()
latency_16 = (end_time - start_time) / 100.0 * 1000
print(f"Yoga 16 Model - Inference Latency: {latency_16:.2f} ms / sample")
