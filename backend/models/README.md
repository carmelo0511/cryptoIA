# CryptoAI Vision Transformer Models

## Model Files

This directory contains the trained Vision Transformer models for crypto chart pattern recognition.

### Required Files

- `crypto_pattern_model_v14.onnx` (327.5 MB) - Production ONNX model for Lambda deployment
- `best_model.pth` (327 MB) - PyTorch checkpoint with best validation accuracy

### Download Instructions

⚠️ **Model files are excluded from git due to size limits (327MB > 100MB GitHub limit)**

**Option 1: From Google Colab Training Session**
1. Download files from your Colab training session
2. Place them in this directory

**Option 2: Regenerate Models**
```bash
cd training/
# Upload to Google Colab and run:
python train_vision_transformer.py
# Or run locally with GPU
```

### Model Performance
- **Validation Accuracy**: 90.5%
- **Pattern Classes**: 10 (head_and_shoulders, double_top, etc.)
- **Input Size**: 224x224 RGB images
- **Framework**: PyTorch + Hugging Face Transformers

### Usage
```python
# ONNX Inference
import onnxruntime
session = onnxruntime.InferenceSession('crypto_pattern_model_v14.onnx')
predictions = session.run(None, {'input.1': image_tensor})
```

### Verification
Run the test script to verify models are working:
```bash
python test_model.py
```