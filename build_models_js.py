import base64
import os

def build_models_js():
    os.makedirs('static', exist_ok=True)
    
    with open('yoga82.onnx', 'rb') as f:
        y82 = base64.b64encode(f.read()).decode('utf-8')
        
    with open('yoga16.onnx', 'rb') as f:
        y16 = base64.b64encode(f.read()).decode('utf-8')
        
    js_content = f"""// AUTO-GENERATED: Base64 Encoded ONNX Models for DUAL-Pose
// This bypasses CORS for local file execution.

const YOGA_82_ONNX_BASE64 = "{y82}";
const YOGA_16_ONNX_BASE64 = "{y16}";

// Helper to convert base64 to Uint8Array for onnxruntime-web
function base64ToUint8Array(base64) {{
    const binaryString = window.atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {{
        bytes[i] = binaryString.charCodeAt(i);
    }}
    return bytes;
}}
"""
    with open('static/models.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print("Successfully built static/models.js")

if __name__ == '__main__':
    build_models_js()
