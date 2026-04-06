import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASETS = {
    "yoga82": {
        "num_classes"        : 82,
        "skeleton_data_root" : os.path.join(BASE_DIR, "skeletons", "yoga82"),
        "batch_size"         : 64,
        "lr"                 : 1e-3,
        "weight_decay"       : 1e-4,
        "epochs"             : 300,
        "patience"           : 30,
    },
    "yoga16": {
        "num_classes"        : 16,
        "skeleton_data_root" : os.path.join(BASE_DIR, "skeletons", "yoga16"),
        "batch_size"         : 32,
        "lr"                 : 1e-3,
        "weight_decay"       : 1e-4,
        "epochs"             : 300,
        "patience"           : 30,
    },
}

MODEL = {
    "num_joints"     : 33,    # BlazePose landmarks
    "gcn_hidden"     : 32,    # GCN hidden dim
    "mlp_hidden"     : 64,    # MLP hidden dim
    "embed_dim"      : 64,    # per-branch embedding dim before fusion
    "num_views"      : 16,    # synthetic yaw-rotation views
    "use_visibility" : False, # include BlazePose visibility score
    "dropout"        : 0.3,
}

GLOBAL_FEAT_DIM = 113  # 33*3 joint coords + 14 limb angles
CHECKPOINT_DIR  = os.path.join(BASE_DIR, "checkpoints")
RESULTS_DIR     = os.path.join(BASE_DIR, "results")
