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
    try:
        import mediapipe as mp
        connections = list(mp.solutions.pose.POSE_CONNECTIONS)
    except Exception:
        connections = []

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

def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

class DualPose(nn.Module):
    def __init__(self, num_classes: int, **kwargs):
        super().__init__()
        # Creating model according to user's specified hyperparameters
        self.model = GCN_Attention_MLP(
            input_dim=212,
            num_nodes=33,
            gcn_hidden=96,
            global_feat_dim=113,
            global_hidden=64,
            latent_dim=128,
            clf_hidden=64,
            num_classes=num_classes
        )

    def forward(self, kp_views, gf_views):
        B, V = kp_views.shape[:2]
        kp_flat = kp_views.reshape(B, V, -1)
        x = torch.cat([kp_flat, gf_views], dim=-1) # [B, 16, 212]
        return self.model(x)
