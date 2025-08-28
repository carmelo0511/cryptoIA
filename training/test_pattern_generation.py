#!/usr/bin/env python3
"""
Test Script for Pattern Generation
==================================

Test the pattern generation functionality locally before full training.
This script generates sample patterns and visualizes them to ensure quality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io

# Import the generator from our training script
try:
    from train_vision_transformer import ChartPatternGenerator, PATTERN_CLASSES
    print("✅ Successfully imported ChartPatternGenerator")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_pattern_generation():
    """Test all pattern generation functions"""
    print("🧪 Testing Pattern Generation...")
    
    generator = ChartPatternGenerator(image_size=(224, 224))
    
    # Create visualization grid
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    axes = axes.ravel()
    
    success_count = 0
    
    for class_id in range(10):
        pattern_name = PATTERN_CLASSES[class_id]
        print(f"  Generating {pattern_name}...")
        
        try:
            # Generate pattern
            pattern_img = generator.generate_pattern(class_id)
            
            # Display in subplot
            axes[class_id].imshow(pattern_img)
            axes[class_id].set_title(f"{class_id}: {pattern_name}", fontsize=10)
            axes[class_id].axis('off')
            
            success_count += 1
            print(f"  ✅ {pattern_name} generated successfully")
            
        except Exception as e:
            print(f"  ❌ Error generating {pattern_name}: {e}")
            axes[class_id].text(0.5, 0.5, f"Error\n{pattern_name}", 
                               ha='center', va='center', transform=axes[class_id].transAxes)
            axes[class_id].set_title(f"{class_id}: {pattern_name} (Error)", fontsize=10)
    
    plt.tight_layout()
    plt.savefig('pattern_samples.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n📊 Results: {success_count}/10 patterns generated successfully")
    print(f"💾 Sample patterns saved as 'pattern_samples.png'")
    
    return success_count == 10

def test_dataset_creation():
    """Test dataset creation with small sample"""
    print("\n🔄 Testing Dataset Creation...")
    
    try:
        # Import dataset class
        from train_vision_transformer import ChartPatternDataset
        
        # Create small test dataset
        print("  Creating test dataset (50 samples)...")
        test_dataset = ChartPatternDataset(size=50, transform=None)
        
        print(f"  ✅ Dataset created: {len(test_dataset)} samples")
        
        # Test a few samples
        print("  Testing sample access...")
        for i in range(min(5, len(test_dataset))):
            img, label = test_dataset[i]
            pattern_name = PATTERN_CLASSES[label]
            print(f"    Sample {i}: {pattern_name} (class {label})")
            
            # Verify image is PIL Image
            if isinstance(img, Image.Image):
                print(f"      ✅ Valid PIL Image: {img.size}")
            else:
                print(f"      ❌ Invalid image type: {type(img)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Dataset creation error: {e}")
        return False

def test_model_loading():
    """Test model loading (requires internet)"""
    print("\n🧠 Testing Model Loading...")
    
    try:
        import torch
        from transformers import ViTForImageClassification
        
        print("  Loading Vision Transformer...")
        model = ViTForImageClassification.from_pretrained(
            'google/vit-base-patch16-224-in21k',
            num_labels=10,
            ignore_mismatched_sizes=True
        )
        
        print(f"  ✅ Model loaded successfully")
        print(f"  📊 Parameters: {sum(p.numel() for p in model.parameters()):,}")
        
        # Test forward pass
        dummy_input = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            outputs = model(dummy_input)
            predictions = outputs.logits
            
        print(f"  ✅ Forward pass successful: {predictions.shape}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model loading error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 CryptoAI Pattern Generation Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Pattern Generation
    if test_pattern_generation():
        tests_passed += 1
        print("✅ Test 1 PASSED: Pattern Generation")
    else:
        print("❌ Test 1 FAILED: Pattern Generation")
    
    print("-" * 30)
    
    # Test 2: Dataset Creation  
    if test_dataset_creation():
        tests_passed += 1
        print("✅ Test 2 PASSED: Dataset Creation")
    else:
        print("❌ Test 2 FAILED: Dataset Creation")
    
    print("-" * 30)
    
    # Test 3: Model Loading
    if test_model_loading():
        tests_passed += 1
        print("✅ Test 3 PASSED: Model Loading")
    else:
        print("❌ Test 3 FAILED: Model Loading")
    
    print("=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🚀 ALL TESTS PASSED! Ready for full training.")
        print("📋 Next Steps:")
        print("  1. Upload train_vision_transformer.py to Google Colab")
        print("  2. Enable GPU runtime")
        print("  3. Run full training pipeline")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before training.")
        return False

if __name__ == "__main__":
    main()