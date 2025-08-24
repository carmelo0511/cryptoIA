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

### Deployed Infrastructure
- **API Base URL:** `https://pbqj4cxv71.execute-api.us-east-1.amazonaws.com/dev`
- **AWS Account:** 304783065136 (us-east-1)
- **Last Updated:** August 24, 2025

### Available Endpoints
```bash
# Test the live API
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

### Next Steps
**Phase 2:** Vision Transformer Training & Integration (Weeks 3-4)

See [ROADMAP.md](./ROADMAP.md) for complete project tracking and implementation details.