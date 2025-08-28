#!/usr/bin/env python3
"""
CryptoAI Vision Transformer Training Script
===========================================

This script creates a labeled dataset of crypto chart patterns and trains a Vision Transformer
for pattern recognition. Designed to run in Google Colab with GPU acceleration.

Key Features:
- Auto-generates 500+ synthetic chart patterns
- Implements Vision Transformer for pattern detection
- Exports quantized ONNX model for Lambda deployment
- Target accuracy: 75-85%

Pattern Classes:
1. Head and Shoulders
2. Double Top
3. Double Bottom
4. Ascending Triangle
5. Descending Triangle
6. Cup and Handle
7. Bullish Flag
8. Bearish Flag
9. Support/Resistance
10. Breakout

Usage in Google Colab:
1. Upload this file to Colab
2. Run with GPU runtime (Runtime -> Change runtime type -> GPU)
3. Execute all cells
4. Download the trained model files
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from transformers import ViTForImageClassification, ViTImageProcessor
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw
import io
import random
import os
from sklearn.metrics import accuracy_score, classification_report
import onnx
import onnxruntime
from torch.quantization import quantize_dynamic

# Check if we're in Colab
try:
    import google.colab
    IN_COLAB = True
    print("🔥 Running in Google Colab - GPU acceleration available!")
except ImportError:
    IN_COLAB = False
    print("💻 Running locally")

# Install required packages (for Colab)
if IN_COLAB:
    os.system("pip install transformers torch torchvision onnx onnxruntime matplotlib pillow scikit-learn")

# Configuration
CONFIG = {
    'image_size': (224, 224),
    'num_classes': 10,
    'batch_size': 32,
    'num_epochs': 15,
    'learning_rate': 1e-4,
    'dataset_size': 1000,  # 100 images per class
    'model_name': 'google/vit-base-patch16-224-in21k',
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

print(f"🚀 Device: {CONFIG['device']}")
print(f"📊 Target dataset size: {CONFIG['dataset_size']} images")

# Pattern class definitions
PATTERN_CLASSES = {
    0: 'head_and_shoulders',
    1: 'double_top', 
    2: 'double_bottom',
    3: 'ascending_triangle',
    4: 'descending_triangle', 
    5: 'cup_and_handle',
    6: 'bullish_flag',
    7: 'bearish_flag',
    8: 'support_resistance',
    9: 'breakout'
}

class ChartPatternGenerator:
    """Generates synthetic crypto chart patterns for training"""
    
    def __init__(self, image_size=(224, 224)):
        self.image_size = image_size
        self.width, self.height = image_size
    
    def _create_base_chart(self):
        """Create base chart with grid and axes"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        ax.tick_params(colors='white')
        return fig, ax
    
    def _add_noise(self, y_values, noise_level=2):
        """Add realistic price noise to smooth patterns"""
        noise = np.random.normal(0, noise_level, len(y_values))
        return y_values + noise
    
    def generate_head_and_shoulders(self):
        """Generate Head and Shoulders pattern"""
        fig, ax = self._create_base_chart()
        
        # Create pattern points
        x = np.array([10, 25, 40, 55, 70, 85])
        y = np.array([30, 45, 35, 55, 40, 30])  # Classic H&S shape
        y = self._add_noise(y)
        
        ax.plot(x, y, 'lime', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='lime')
        
        # Add volume bars
        volume_x = np.linspace(10, 85, 15)
        volume_y = np.random.uniform(5, 15, 15)
        ax.bar(volume_x, volume_y, width=3, alpha=0.6, color='cyan')
        
        return self._fig_to_pil(fig)
    
    def generate_double_top(self):
        """Generate Double Top pattern"""
        fig, ax = self._create_base_chart()
        
        x = np.array([15, 30, 45, 60, 75])
        y = np.array([25, 55, 35, 55, 30])  # Two peaks
        y = self._add_noise(y)
        
        ax.plot(x, y, 'red', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='red')
        
        volume_x = np.linspace(15, 75, 12)
        volume_y = np.random.uniform(3, 12, 12)
        ax.bar(volume_x, volume_y, width=3, alpha=0.6, color='orange')
        
        return self._fig_to_pil(fig)
    
    def generate_double_bottom(self):
        """Generate Double Bottom pattern"""
        fig, ax = self._create_base_chart()
        
        x = np.array([15, 30, 45, 60, 75])
        y = np.array([65, 35, 55, 35, 60])  # Two valleys
        y = self._add_noise(y)
        
        ax.plot(x, y, 'lime', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='lime')
        
        volume_x = np.linspace(15, 75, 12)
        volume_y = np.random.uniform(3, 12, 12)
        ax.bar(volume_x, volume_y, width=3, alpha=0.6, color='cyan')
        
        return self._fig_to_pil(fig)
    
    def generate_ascending_triangle(self):
        """Generate Ascending Triangle pattern"""
        fig, ax = self._create_base_chart()
        
        # Higher lows, same highs
        x = np.linspace(20, 80, 8)
        y_highs = np.full(4, 60) + np.random.normal(0, 1, 4)
        y_lows = np.linspace(25, 45, 4) + np.random.normal(0, 1, 4)
        
        y = []
        for i in range(4):
            y.extend([y_lows[i], y_highs[i]])
        
        ax.plot(x, y, 'yellow', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='yellow')
        
        # Draw triangle lines
        ax.plot([20, 80], [60, 60], 'white', linewidth=1, linestyle='--')
        ax.plot([20, 80], [25, 45], 'white', linewidth=1, linestyle='--')
        
        return self._fig_to_pil(fig)
    
    def generate_descending_triangle(self):
        """Generate Descending Triangle pattern"""
        fig, ax = self._create_base_chart()
        
        # Lower highs, same lows
        x = np.linspace(20, 80, 8)
        y_lows = np.full(4, 30) + np.random.normal(0, 1, 4)
        y_highs = np.linspace(65, 45, 4) + np.random.normal(0, 1, 4)
        
        y = []
        for i in range(4):
            y.extend([y_lows[i], y_highs[i]])
        
        ax.plot(x, y, 'orange', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='orange')
        
        # Draw triangle lines
        ax.plot([20, 80], [30, 30], 'white', linewidth=1, linestyle='--')
        ax.plot([20, 80], [65, 45], 'white', linewidth=1, linestyle='--')
        
        return self._fig_to_pil(fig)
    
    def generate_cup_and_handle(self):
        """Generate Cup and Handle pattern"""
        fig, ax = self._create_base_chart()
        
        # Cup shape with handle
        x1 = np.linspace(10, 60, 25)
        y1 = 50 - 20 * np.sin(np.linspace(0, np.pi, 25)) ** 2
        
        x2 = np.linspace(60, 80, 10)
        y2 = np.linspace(50, 45, 10)
        
        x = np.concatenate([x1, x2])
        y = np.concatenate([y1, y2])
        y = self._add_noise(y)
        
        ax.plot(x, y, 'cyan', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='cyan')
        
        return self._fig_to_pil(fig)
    
    def generate_bullish_flag(self):
        """Generate Bullish Flag pattern"""
        fig, ax = self._create_base_chart()
        
        # Sharp rise followed by consolidation
        x1 = np.linspace(10, 30, 10)
        y1 = np.linspace(25, 65, 10)
        
        x2 = np.linspace(30, 70, 20)
        y2 = 65 + 3 * np.sin(np.linspace(0, 4*np.pi, 20)) - np.linspace(0, 8, 20)
        
        x = np.concatenate([x1, x2])
        y = np.concatenate([y1, y2])
        y = self._add_noise(y)
        
        ax.plot(x, y, 'lime', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='lime')
        
        return self._fig_to_pil(fig)
    
    def generate_bearish_flag(self):
        """Generate Bearish Flag pattern"""
        fig, ax = self._create_base_chart()
        
        # Sharp fall followed by consolidation
        x1 = np.linspace(10, 30, 10)
        y1 = np.linspace(75, 35, 10)
        
        x2 = np.linspace(30, 70, 20)
        y2 = 35 + 3 * np.sin(np.linspace(0, 4*np.pi, 20)) + np.linspace(0, 8, 20)
        
        x = np.concatenate([x1, x2])
        y = np.concatenate([y1, y2])
        y = self._add_noise(y)
        
        ax.plot(x, y, 'red', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='red')
        
        return self._fig_to_pil(fig)
    
    def generate_support_resistance(self):
        """Generate Support/Resistance pattern"""
        fig, ax = self._create_base_chart()
        
        # Price bouncing off support/resistance levels
        x = np.linspace(10, 90, 50)
        y = 45 + 10 * np.sin(x/10) + np.random.normal(0, 2, 50)
        
        # Ensure bounces off 40 and 60 levels
        y = np.clip(y, 25, 75)
        for i in range(len(y)):
            if y[i] < 30:
                y[i] = 30 + abs(np.random.normal(0, 2))
            elif y[i] > 70:
                y[i] = 70 - abs(np.random.normal(0, 2))
        
        ax.plot(x, y, 'white', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='white')
        
        # Draw support/resistance lines
        ax.axhline(y=30, color='red', linestyle='--', alpha=0.7, label='Support')
        ax.axhline(y=70, color='lime', linestyle='--', alpha=0.7, label='Resistance')
        
        return self._fig_to_pil(fig)
    
    def generate_breakout(self):
        """Generate Breakout pattern"""
        fig, ax = self._create_base_chart()
        
        # Consolidation followed by breakout
        x1 = np.linspace(10, 60, 30)
        y1 = 45 + 5 * np.sin(x1/5) + np.random.normal(0, 1, 30)
        
        x2 = np.linspace(60, 85, 15)
        y2 = np.linspace(50, 75, 15) + np.random.normal(0, 2, 15)
        
        x = np.concatenate([x1, x2])
        y = np.concatenate([y1, y2])
        
        ax.plot(x, y, 'yellow', linewidth=2)
        ax.fill_between(x, y, alpha=0.1, color='yellow')
        
        # Breakout point
        ax.axvline(x=60, color='red', linestyle='--', alpha=0.8)
        ax.text(62, 80, 'BREAKOUT', color='red', fontweight='bold')
        
        return self._fig_to_pil(fig)
    
    def _fig_to_pil(self, fig):
        """Convert matplotlib figure to PIL Image"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', 
                   facecolor='black', dpi=100)
        buf.seek(0)
        img = Image.open(buf).convert('RGB')
        plt.close(fig)
        
        # Resize to target size
        img = img.resize(self.image_size, Image.Resampling.LANCZOS)
        return img
    
    def generate_pattern(self, pattern_class):
        """Generate pattern based on class ID"""
        generators = {
            0: self.generate_head_and_shoulders,
            1: self.generate_double_top,
            2: self.generate_double_bottom,
            3: self.generate_ascending_triangle,
            4: self.generate_descending_triangle,
            5: self.generate_cup_and_handle,
            6: self.generate_bullish_flag,
            7: self.generate_bearish_flag,
            8: self.generate_support_resistance,
            9: self.generate_breakout
        }
        
        if pattern_class not in generators:
            raise ValueError(f"Unknown pattern class: {pattern_class}")
        
        return generators[pattern_class]()

class ChartPatternDataset(Dataset):
    """PyTorch Dataset for chart patterns"""
    
    def __init__(self, size=1000, transform=None):
        self.size = size
        self.transform = transform
        self.generator = ChartPatternGenerator(CONFIG['image_size'])
        
        # Pre-generate all samples for consistent training
        print("🔄 Generating dataset...")
        self.images = []
        self.labels = []
        
        samples_per_class = size // CONFIG['num_classes']
        
        for class_id in range(CONFIG['num_classes']):
            for _ in range(samples_per_class):
                img = self.generator.generate_pattern(class_id)
                self.images.append(img)
                self.labels.append(class_id)
        
        print(f"✅ Generated {len(self.images)} samples")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

def create_data_transforms():
    """Create train and validation transforms"""
    train_transform = transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.3),
        transforms.RandomRotation(degrees=5),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform

def create_model():
    """Create and configure Vision Transformer model"""
    model = ViTForImageClassification.from_pretrained(
        CONFIG['model_name'],
        num_labels=CONFIG['num_classes'],
        ignore_mismatched_sizes=True
    )
    
    # Fine-tune only the classifier
    for param in model.vit.parameters():
        param.requires_grad = False
    
    for param in model.classifier.parameters():
        param.requires_grad = True
    
    return model

def train_model(model, train_loader, val_loader):
    """Train the Vision Transformer model"""
    device = CONFIG['device']
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=CONFIG['learning_rate'])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
    
    best_val_acc = 0.0
    train_losses = []
    val_accuracies = []
    
    print("🚀 Starting training...")
    
    for epoch in range(CONFIG['num_epochs']):
        # Training phase
        model.train()
        train_loss = 0.0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs.logits, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
            if batch_idx % 10 == 0:
                print(f'Epoch [{epoch+1}/{CONFIG["num_epochs"]}], '
                      f'Batch [{batch_idx}/{len(train_loader)}], '
                      f'Loss: {loss.item():.4f}')
        
        # Validation phase
        model.eval()
        val_preds = []
        val_labels = []
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.logits, 1)
                val_preds.extend(predicted.cpu().numpy())
                val_labels.extend(labels.cpu().numpy())
        
        val_acc = accuracy_score(val_labels, val_preds)
        avg_train_loss = train_loss / len(train_loader)
        
        train_losses.append(avg_train_loss)
        val_accuracies.append(val_acc)
        
        scheduler.step(avg_train_loss)
        
        print(f'Epoch [{epoch+1}/{CONFIG["num_epochs"]}] - '
              f'Train Loss: {avg_train_loss:.4f}, '
              f'Val Accuracy: {val_acc:.4f}')
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), 'best_model.pth')
            print(f'💾 New best model saved! Accuracy: {val_acc:.4f}')
    
    print(f"\n🏆 Training completed! Best validation accuracy: {best_val_acc:.4f}")
    return best_val_acc, train_losses, val_accuracies

def export_to_onnx(model, sample_input):
    """Export trained model to ONNX format"""
    model.eval()
    
    # Standard ONNX export
    torch.onnx.export(
        model,
        sample_input,
        "crypto_pattern_model.onnx",
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # Quantize for smaller model size
    quantized_model = quantize_dynamic(
        model, {nn.Linear}, dtype=torch.qint8
    )
    
    # Export quantized model
    torch.onnx.export(
        quantized_model,
        sample_input,
        "crypto_pattern_model_quantized.onnx",
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output']
    )
    
    print("✅ Models exported:")
    print("- crypto_pattern_model.onnx (Full model)")
    print("- crypto_pattern_model_quantized.onnx (Quantized model)")
    
    # Test ONNX model
    ort_session = onnxruntime.InferenceSession("crypto_pattern_model_quantized.onnx")
    ort_inputs = {ort_session.get_inputs()[0].name: sample_input.numpy()}
    ort_outputs = ort_session.run(None, ort_inputs)
    
    print("🧪 ONNX model test passed!")
    
    return ort_session

def visualize_predictions(model, test_loader, device):
    """Visualize model predictions on test samples"""
    model.eval()
    
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    axes = axes.ravel()
    
    with torch.no_grad():
        images, labels = next(iter(test_loader))
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.logits, 1)
        
        for i in range(10):
            # Convert tensor to image
            img = images[i].cpu()
            img = img * torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
            img = img + torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
            img = torch.clamp(img, 0, 1)
            img = transforms.ToPILImage()(img)
            
            axes[i].imshow(img)
            axes[i].set_title(f'True: {PATTERN_CLASSES[labels[i].item()]}\n'
                            f'Pred: {PATTERN_CLASSES[predicted[i].item()]}')
            axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig('predictions_visualization.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("📊 Predictions visualization saved as 'predictions_visualization.png'")

def main():
    """Main training pipeline"""
    print("🤖 CryptoAI Vision Transformer Training")
    print("=" * 50)
    print(f"Device: {CONFIG['device']}")
    print(f"Dataset size: {CONFIG['dataset_size']}")
    print(f"Batch size: {CONFIG['batch_size']}")
    print(f"Epochs: {CONFIG['num_epochs']}")
    print("=" * 50)
    
    # Create transforms
    train_transform, val_transform = create_data_transforms()
    
    # Create datasets
    print("\n📚 Creating datasets...")
    train_dataset = ChartPatternDataset(
        size=int(CONFIG['dataset_size'] * 0.8), 
        transform=train_transform
    )
    val_dataset = ChartPatternDataset(
        size=int(CONFIG['dataset_size'] * 0.2), 
        transform=val_transform
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=CONFIG['batch_size'], 
        shuffle=True,
        num_workers=2 if not IN_COLAB else 0
    )
    val_loader = DataLoader(
        val_dataset, 
        batch_size=CONFIG['batch_size'], 
        shuffle=False,
        num_workers=2 if not IN_COLAB else 0
    )
    
    print(f"✅ Train samples: {len(train_dataset)}")
    print(f"✅ Validation samples: {len(val_dataset)}")
    
    # Create model
    print("\n🧠 Loading Vision Transformer...")
    model = create_model()
    print(f"✅ Model loaded: {CONFIG['model_name']}")
    
    # Train model
    best_acc, train_losses, val_accuracies = train_model(model, train_loader, val_loader)
    
    # Load best model for export
    model.load_state_dict(torch.load('best_model.pth'))
    
    # Export to ONNX
    print("\n📦 Exporting to ONNX...")
    sample_input = torch.randn(1, 3, 224, 224).to(CONFIG['device'])
    ort_session = export_to_onnx(model, sample_input)
    
    # Visualize predictions
    print("\n📊 Creating prediction visualizations...")
    visualize_predictions(model, val_loader, CONFIG['device'])
    
    # Final accuracy report
    print("\n" + "=" * 50)
    print("🏆 TRAINING COMPLETE!")
    print(f"🎯 Best Validation Accuracy: {best_acc:.1%}")
    print(f"🎯 Target Accuracy: 75-85%")
    
    if best_acc >= 0.75:
        print("✅ TARGET ACCURACY ACHIEVED!")
    else:
        print("⚠️  Consider training longer or adjusting hyperparameters")
    
    print("\n📁 Generated Files:")
    print("- best_model.pth (PyTorch model)")
    print("- crypto_pattern_model.onnx (ONNX model)")
    print("- crypto_pattern_model_quantized.onnx (Quantized ONNX)")
    print("- predictions_visualization.png (Sample predictions)")
    
    if IN_COLAB:
        print("\n💾 Download these files to your local machine!")
        print("📋 Pattern Classes:")
        for i, pattern in PATTERN_CLASSES.items():
            print(f"   {i}: {pattern}")
    
    return model, ort_session, best_acc

if __name__ == "__main__":
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    
    # Run training
    model, onnx_session, accuracy = main()
    
    print(f"\n🚀 Ready for Phase 3: Backend Integration!")
    print(f"📈 Model accuracy: {accuracy:.1%}")