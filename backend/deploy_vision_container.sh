#!/bin/bash

# Deploy Vision Transformer Lambda Container
echo "🚀 Deploying Vision Transformer Lambda Container"

# Exit on any error
set -e

# Configuration
PROJECT_NAME="cryptoai-analytics"
ENVIRONMENT="dev"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="304783065136"
REPOSITORY_NAME="${PROJECT_NAME}-vision-model"

# Navigate to backend directory
cd "$(dirname "$0")"

echo "📍 Working in directory: $(pwd)"

# Check if required files exist
echo "🔍 Checking required files..."
if [ ! -f "models/crypto_pattern_model_v14.onnx" ]; then
    echo "❌ Error: ONNX model file not found!"
    echo "Expected: models/crypto_pattern_model_v14.onnx"
    exit 1
fi

if [ ! -f "pattern_analysis_vision.py" ]; then
    echo "❌ Error: Vision analysis script not found!"
    exit 1
fi

echo "✅ All required files found"

# Get ECR repository URL from Terraform outputs
echo "🏗️ Getting ECR repository URL from Terraform..."
cd ../infrastructure

# Apply infrastructure changes first (to create ECR if needed)
echo "🔄 Applying Terraform infrastructure updates..."
terraform plan -out=tfplan
terraform apply tfplan

# Get ECR repository URL
ECR_URL=$(terraform output -raw vision_model_ecr_repository_url 2>/dev/null || echo "")

if [ -z "$ECR_URL" ]; then
    echo "⚠️ ECR URL not found in outputs, constructing manually..."
    ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}"
fi

echo "🎯 ECR Repository URL: $ECR_URL"

# Go back to backend directory
cd ../backend

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL

# Build Docker image
echo "🐳 Building Docker image..."
docker build --platform linux/amd64 -t $REPOSITORY_NAME:latest .

# Tag for ECR
echo "🏷️ Tagging image for ECR..."
docker tag $REPOSITORY_NAME:latest $ECR_URL:latest

# Push to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_URL:latest

# Update Lambda function
echo "🔄 Updating Lambda function..."
aws lambda update-function-code \
    --function-name "${PROJECT_NAME}-pattern-analysis-${ENVIRONMENT}" \
    --image-uri "${ECR_URL}:latest" \
    --region $AWS_REGION

# Wait for update to complete
echo "⏳ Waiting for Lambda function update to complete..."
aws lambda wait function-updated \
    --function-name "${PROJECT_NAME}-pattern-analysis-${ENVIRONMENT}" \
    --region $AWS_REGION

echo "✅ Vision Transformer Lambda Container deployed successfully!"

# Test the deployment
echo "🧪 Testing the deployment..."
aws lambda invoke \
    --function-name "${PROJECT_NAME}-pattern-analysis-${ENVIRONMENT}" \
    --payload '{"symbol": "BTCUSDT"}' \
    --region $AWS_REGION \
    response.json

if [ $? -eq 0 ]; then
    echo "✅ Lambda function test invocation successful"
    echo "📋 Response preview:"
    head -n 5 response.json
    rm -f response.json
else
    echo "❌ Lambda function test failed"
    exit 1
fi

echo ""
echo "🎉 Deployment Complete!"
echo "📊 Function: ${PROJECT_NAME}-pattern-analysis-${ENVIRONMENT}"
echo "🎯 ECR Image: ${ECR_URL}:latest"
echo "⚡ Vision Transformer model ready for inference"