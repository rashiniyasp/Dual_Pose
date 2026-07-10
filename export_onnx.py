import torch
import warnings
warnings.filterwarnings('ignore')
from models.dual_pose import GCN_Attention_MLP

print("Exporting Yoga 82...")
model82 = GCN_Attention_MLP(input_dim=212, num_nodes=33, num_classes=82, gcn_hidden=96, clf_hidden=64)
model82.load_state_dict(torch.load("Yoga82_Weights.pth", map_location="cpu"))
model82.eval()
dummy_input = torch.randn(1, 16, 212)
torch.onnx.export(
    model82, dummy_input, "yoga82.onnx", 
    export_params=True, opset_version=14, 
    do_constant_folding=True, 
    input_names=['input'], output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
)

print("Exporting Yoga 16...")
model16 = GCN_Attention_MLP(input_dim=212, num_nodes=33, num_classes=16, gcn_hidden=96, clf_hidden=64)
model16.load_state_dict(torch.load("Yoga16_Weights.pth", map_location="cpu"))
model16.eval()
torch.onnx.export(
    model16, dummy_input, "yoga16.onnx", 
    export_params=True, opset_version=14, 
    do_constant_folding=True, 
    input_names=['input'], output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
)

print("Done exporting to ONNX!")
