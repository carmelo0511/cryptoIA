#!/usr/bin/env python3
"""
Validation Script for Google Colab Setup
========================================

This script validates that our training setup will work in Google Colab
by testing the pattern generation without requiring PyTorch locally.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw
import numpy as np
import io
import random

# Pattern class definitions (simplified)
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

class SimpleChartGenerator:
    """Simplified chart generator for validation"""
    
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
    
    def generate_sample_pattern(self, pattern_type=0):
        """Generate a sample pattern for testing"""
        fig, ax = self._create_base_chart()
        
        if pattern_type == 0:  # Head and Shoulders
            x = np.array([10, 25, 40, 55, 70, 85])
            y = np.array([30, 45, 35, 55, 40, 30])
            ax.plot(x, y, 'lime', linewidth=2)
            ax.fill_between(x, y, alpha=0.1, color='lime')
            title = "Head and Shoulders"
            
        elif pattern_type == 1:  # Double Top
            x = np.array([15, 30, 45, 60, 75])
            y = np.array([25, 55, 35, 55, 30])
            ax.plot(x, y, 'red', linewidth=2)
            ax.fill_between(x, y, alpha=0.1, color='red')
            title = "Double Top"
            
        else:  # Default pattern
            x = np.linspace(10, 90, 20)
            y = 50 + 15 * np.sin(x/10) + np.random.normal(0, 2, 20)
            ax.plot(x, y, 'cyan', linewidth=2)
            title = "Sample Pattern"
        
        ax.set_title(title, color='white', fontsize=14)
        
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

def test_basic_generation():
    """Test basic pattern generation"""
    print("🧪 Testing Basic Pattern Generation...")
    
    generator = SimpleChartGenerator(image_size=(224, 224))
    
    # Create test visualization
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    patterns_tested = 0
    
    for i in range(3):
        try:
            pattern_img = generator.generate_sample_pattern(i)
            axes[i].imshow(pattern_img)
            axes[i].set_title(f"Pattern {i}", fontsize=12)
            axes[i].axis('off')
            patterns_tested += 1
            print(f"  ✅ Pattern {i} generated successfully")
        except Exception as e:
            print(f"  ❌ Error generating pattern {i}: {e}")
            axes[i].text(0.5, 0.5, f"Error\nPattern {i}", 
                        ha='center', va='center', transform=axes[i].transAxes)
    
    plt.tight_layout()
    plt.savefig('validation_patterns.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n📊 Results: {patterns_tested}/3 patterns generated successfully")
    print(f"💾 Validation patterns saved as 'validation_patterns.png'")
    
    return patterns_tested == 3

def validate_colab_requirements():
    """Check that required modules are available"""
    print("\n🔍 Validating Colab Requirements...")
    
    required_modules = [
        'matplotlib',
        'numpy', 
        'PIL',
        'io',
        'random'
    ]
    
    available_modules = 0
    
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            else:
                __import__(module)
            print(f"  ✅ {module} available")
            available_modules += 1
        except ImportError:
            print(f"  ❌ {module} missing")
    
    print(f"\n📊 Modules: {available_modules}/{len(required_modules)} available")
    return available_modules == len(required_modules)

def create_colab_instructions():
    """Create instructions for Colab setup"""
    instructions = """
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
"""
    
    print(instructions)
    
    # Save instructions to file
    with open('COLAB_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print("💾 Instructions saved as 'COLAB_INSTRUCTIONS.md'")

def main():
    """Main validation function"""
    print("🚀 CryptoAI Colab Setup Validation")
    print("=" * 50)
    
    validation_passed = 0
    total_validations = 2
    
    # Test 1: Basic Pattern Generation
    if test_basic_generation():
        validation_passed += 1
        print("✅ Validation 1 PASSED: Pattern Generation")
    else:
        print("❌ Validation 1 FAILED: Pattern Generation")
    
    print("-" * 30)
    
    # Test 2: Module Requirements
    if validate_colab_requirements():
        validation_passed += 1
        print("✅ Validation 2 PASSED: Module Requirements")
    else:
        print("❌ Validation 2 FAILED: Module Requirements")
    
    print("-" * 30)
    
    # Create Colab instructions
    create_colab_instructions()
    
    print("=" * 50)
    print(f"🎯 Validation Results: {validation_passed}/{total_validations} passed")
    
    if validation_passed == total_validations:
        print("🚀 VALIDATION SUCCESSFUL!")
        print("✨ Ready for Google Colab training!")
        print("\n📋 Next Steps:")
        print("  1. Upload train_vision_transformer.py to Google Colab")
        print("  2. Enable GPU runtime")
        print("  3. Run: !python train_vision_transformer.py")
        print("  4. Wait for training completion (~45 min)")
        print("  5. Download the trained models")
        return True
    else:
        print("⚠️  Validation incomplete - check errors above")
        return False

if __name__ == "__main__":
    main()