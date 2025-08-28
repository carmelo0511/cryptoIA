# CryptoAI Analytics

A scalable AI platform for crypto market analysis with real-time pattern detection using Vision Transformers.

## Project Structure

```
cryptoIA/
├── README.md              # Project overview
├── ROADMAP.md            # Detailed implementation roadmap
├── infrastructure/       # Terraform AWS infrastructure
├── backend/             # Serverless Lambda functions
├── frontend/            # React dashboard with Canvas overlay
├── training/            # Vision Transformer training scripts
├── data/               # Dataset and chart generation
└── docs/               # Documentation and portfolio materials
```

## Quick Start

See [ROADMAP.md](./ROADMAP.md) for detailed implementation plan.

## Tech Stack

- **Backend:** AWS Lambda, DynamoDB, S3, API Gateway
- **Frontend:** React, Canvas API
- **AI/ML:** Vision Transformer (ViT), ONNX
- **Infrastructure:** Terraform, CloudWatch
- **Training:** Google Colab

## 🚀 Live Deployment Status

**✅ Phase 1 COMPLETED** - Infrastructure & Data Pipeline fully operational  
**✅ Phase 2 COMPLETED** - Vision Transformer Training & Model Export

### Current Status
- **Phase 1:** AWS Infrastructure deployed and operational
- **Phase 2:** Vision Transformer trained with **90.5% accuracy** 
- **Next:** Phase 3 - Backend & AI Integration

### Deployed Infrastructure
- **API Base URL:** `https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev`
- **AWS Account:** 304783065136 (us-east-1)
- **Last Updated:** August 27, 2025

### Available Endpoints
```bash
# Test the live API infrastructure
curl "https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev/predictions"
curl "https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev/patterns?symbol=BTCUSDT"
```

### AWS Resources Deployed
- ✅ **3 Lambda Functions** (API, Data Ingestion, Pattern Analysis)
- ✅ **API Gateway** with REST endpoints and caching
- ✅ **3 DynamoDB Tables** with TTL for data management
- ✅ **2 S3 Buckets** with encryption and lifecycle policies
- ✅ **IAM Roles & Policies** for secure access
- ✅ **CloudWatch Logs** for monitoring

### Vision Transformer Models
- ✅ **Training Completed:** 90.5% validation accuracy (exceeded 75-85% target)
- ✅ **Model Files:** Available via Git LFS
  - `backend/models/crypto_pattern_model_v14.onnx` (327.5MB) - Production ready
  - `backend/models/best_model.pth` (327MB) - PyTorch checkpoint
- ✅ **Pattern Classes:** 10 crypto chart patterns implemented
- ✅ **Training Infrastructure:** Google Colab notebook + local scripts
- ✅ **Verification:** All tests passed (ONNX inference, pattern recognition)

### Next Steps
**Phase 3:** Backend & AI Integration - Deploy Lambda Container for Vision inference

See [ROADMAP.md](./ROADMAP.md) for complete project tracking and implementation details.