
📋 Google Colab Setup Instructions
=================================

1. **Open Google Colab**
   - Go to: https://colab.research.google.com
   - File → New notebook

2. **Enable GPU**
   - Runtime → Change runtime type
   - Hardware accelerator → GPU
   - Save

3. **Upload Files**
   - Click folder icon (left panel)
   - Upload: train_vision_transformer.py
   - Or upload: CryptoAI_Vision_Training.ipynb

4. **Run Training**
   Method A (Script): !python train_vision_transformer.py
   Method B (Notebook): Run all cells

5. **Expected Results**
   - Training time: 30-60 minutes
   - Target accuracy: 75-85%
   - Model files: .onnx, .pth
   - Visualization: predictions.png

6. **Download Results**
   - crypto_pattern_model_quantized.onnx (for production)
   - best_model.pth (full model)
   - predictions_visualization.png (samples)
