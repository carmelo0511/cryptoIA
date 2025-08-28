# 🤖 CryptoAI Vision Transformer Training

## Overview

Cette phase implémente l'entraînement d'un Vision Transformer pour la reconnaissance de patterns techniques dans les graphiques crypto. Le système génère automatiquement un dataset de 1000+ images synthétiques et entraîne un modèle ViT avec une précision cible de 75-85%.

## 🎯 Pattern Classes

| ID | Pattern | Description |
|----|---------|-------------|
| 0 | Head and Shoulders | Pattern de retournement baissier classique |
| 1 | Double Top | Confirmation de résistance et retournement |
| 2 | Double Bottom | Confirmation de support et rebond |
| 3 | Ascending Triangle | Consolidation avec breakout haussier |
| 4 | Descending Triangle | Consolidation avec breakout baissier |
| 5 | Cup and Handle | Pattern de continuation haussière |
| 6 | Bullish Flag | Correction temporaire en tendance haussière |
| 7 | Bearish Flag | Correction temporaire en tendance baissière |
| 8 | Support/Resistance | Niveaux techniques de rebond |
| 9 | Breakout | Sortie de phase de consolidation |

## 🚀 Quick Start (Google Colab)

### Méthode 1: Notebook Colab (Recommandé)
1. Ouvrir Google Colab
2. Upload `CryptoAI_Vision_Training.ipynb`
3. Runtime → Change runtime type → GPU
4. Upload `train_vision_transformer.py`
5. Exécuter toutes les cellules

### Méthode 2: Script Direct
1. Upload `train_vision_transformer.py` dans Colab
2. Exécuter: `!python train_vision_transformer.py`

## 💻 Local Training

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement de l'entraînement
python train_vision_transformer.py
```

**⚠️ Attention**: L'entraînement local nécessite un GPU avec au moins 4GB VRAM.

## 📊 Architecture du Modèle

```
Vision Transformer (ViT-Base)
├── Patch Embedding (16x16 patches)
├── Transformer Encoder (12 layers)
├── Classification Head (10 classes)
└── Output: Pattern probabilities
```

### Caractéristiques:
- **Base Model**: `google/vit-base-patch16-224-in21k`
- **Input Size**: 224x224 RGB
- **Quantification**: INT8 pour optimisation Lambda
- **Model Size**: ~50MB (quantifié)

## 🔧 Configuration

```python
CONFIG = {
    'image_size': (224, 224),
    'num_classes': 10,
    'batch_size': 32,
    'num_epochs': 15,
    'learning_rate': 1e-4,
    'dataset_size': 1000,
    'model_name': 'google/vit-base-patch16-224-in21k'
}
```

## 📈 Dataset Generation

Le générateur crée automatiquement des patterns synthétiques avec:
- **Réalisme**: Bruit de prix, volumes, grilles
- **Variabilité**: Rotations, couleurs, échelles
- **Labeling**: Classification automatique
- **Qualité**: Charts haute résolution (224x224)

### Exemple de génération:

```python
generator = ChartPatternGenerator()
head_shoulders = generator.generate_head_and_shoulders()
double_top = generator.generate_double_top()
```

## 🧪 Evaluation

### Métriques:
- **Accuracy**: % de prédictions correctes
- **Validation Split**: 80% train / 20% validation
- **Target**: 75-85% accuracy
- **Visualization**: Sample predictions avec ground truth

### Test du modèle ONNX:
```python
import onnxruntime

ort_session = onnxruntime.InferenceSession('crypto_pattern_model_quantized.onnx')
predictions = ort_session.run(None, {'input': test_image})
```

## 📁 Output Files

Après entraînement:
```
training/
├── best_model.pth                     # PyTorch model (full)
├── crypto_pattern_model.onnx          # ONNX model (full)
├── crypto_pattern_model_quantized.onnx # ONNX quantized (production)
└── predictions_visualization.png      # Sample predictions
```

## 🔄 Training Pipeline

1. **Dataset Generation** (5 min)
   - 1000 images synthétiques
   - 10 classes de patterns
   - Augmentation de données

2. **Model Loading** (1 min)
   - Vision Transformer pré-entraîné
   - Fine-tuning du classifier

3. **Training Loop** (15-30 min sur GPU)
   - 15 epochs avec early stopping
   - Validation à chaque epoch
   - Sauvegarde du meilleur modèle

4. **Export & Quantization** (2 min)
   - Export ONNX standard
   - Quantification INT8
   - Validation du modèle

## 💡 Tips & Optimizations

### Pour améliorer la précision:
- Augmenter `num_epochs` à 25-30
- Réduire `learning_rate` à 5e-5
- Augmenter `dataset_size` à 2000+
- Ajouter plus d'augmentations

### Pour réduire la taille du modèle:
- Utiliser ViT-Small: `google/vit-small-patch16-224`
- Quantification plus agressive
- Pruning des couches

## 🚀 Next Phase

Une fois l'entraînement terminé avec succès (>75% accuracy):

**Phase 3: Backend Integration**
- Deploy modèle ONNX dans Lambda Container
- API endpoints pour inférence en temps réel
- Tests end-to-end avec données crypto réelles

## 📋 Checklist Phase 2

- [x] Script d'entraînement créé
- [x] Notebook Colab préparé  
- [x] Générateur de patterns implémenté
- [ ] **Exécuter l'entraînement sur GPU**
- [ ] **Validation de la précision (>75%)**
- [ ] **Export ONNX quantifié**
- [ ] **Téléchargement des modèles**

---

**⏱️ Temps estimé**: 45-60 minutes sur Google Colab (GPU gratuit)  
**💰 Coût**: 0€ (Colab gratuit) ou ~5€ (Colab Pro pour GPU plus rapide)