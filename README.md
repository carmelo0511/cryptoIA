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
**✅ Phase 3 COMPLETED** - Backend & AI Integration with Docker Container

### Current Status
- **Phase 1:** AWS Infrastructure deployed and operational ✅
- **Phase 2:** Vision Transformer trained with **90.5% accuracy** ✅
- **Phase 3:** Docker Container deployment with ONNX Vision model ✅
- **Next:** Phase 4 - Frontend Dashboard Development

### Deployed Infrastructure
- **API Base URL:** `https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev`
- **AWS Account:** 304783065136 (us-east-1)
- **Container Registry:** ECR with Vision Transformer images
- **Cost Optimized:** API Gateway caching disabled (-$14.40/month)
- **Budget Control:** $10/month limit with 80% alerts
- **Last Updated:** August 28, 2025

### Available Endpoints
```bash
# Test the live API infrastructure
curl "https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev/predictions"
curl "https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev/patterns?symbol=BTCUSDT"

# Vision-based pattern analysis (Phase 3)
curl -X POST "https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev/analyze-chart" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT"}'
```

### AWS Resources Deployed
- ✅ **3 Lambda Functions** (API, Data Ingestion, Pattern Analysis)
- ✅ **ECR Repository** with Vision Transformer container images
- ✅ **API Gateway** with REST endpoints (cost-optimized)
- ✅ **3 DynamoDB Tables** with TTL for data management
- ✅ **2 S3 Buckets** with encryption and lifecycle policies
- ✅ **IAM Roles & Policies** for secure access
- ✅ **CloudWatch Logs** for monitoring and debugging
- ✅ **Budget & Cost Controls** for expense management

### Vision Transformer Container
- ✅ **Docker Container:** Lambda-compatible with ONNX runtime
- ✅ **Model Integration:** 327MB ONNX model in production container
- ✅ **ECR Deployment:** Images pushed to `cryptoai-analytics-vision-model`
- ✅ **Performance:** Optimized for <100ms inference latency
- ✅ **Scalability:** Auto-scaling Lambda container architecture

### Vision Transformer Models
- ✅ **Training Completed:** 90.5% validation accuracy (exceeded 75-85% target)
- ✅ **Model Files:** Available via Git LFS
  - `backend/models/crypto_pattern_model_v14.onnx` (327.5MB) - Production ready
  - `backend/models/best_model.pth` (327MB) - PyTorch checkpoint
- ✅ **Pattern Classes:** 10 crypto chart patterns implemented
- ✅ **Training Infrastructure:** Google Colab notebook + local scripts
- ✅ **Verification:** All tests passed (ONNX inference, pattern recognition)
- ✅ **Container Integration:** Working Docker deployment pipeline

### Next Steps
**Phase 4:** Frontend Dashboard - React interface for real-time pattern visualization

See [ROADMAP.md](./ROADMAP.md) for complete project tracking and implementation details.