#!/bin/bash

# Deploy script for Lambda functions
set -e

echo "Building Lambda deployment packages..."

# Create dist directory
mkdir -p dist

# Function to create deployment package
create_package() {
    local function_name=$1
    local python_file=$2
    
    echo "Creating package for $function_name..."
    
    # Create temporary directory
    temp_dir=$(mktemp -d)
    
    # Install dependencies
    pip3 install -r requirements_basic.txt -t $temp_dir
    
    # Copy function code
    cp $python_file $temp_dir/index.py
    
    # Create zip package
    cd $temp_dir
    zip -r "/Users/bryannakache/portfolio/cryptoIA-1/backend/dist/$function_name.zip" .
    cd - > /dev/null
    
    # Cleanup
    rm -rf $temp_dir
    
    echo "Package created: dist/$function_name.zip"
}

# Create packages for each Lambda function
create_package "data-ingestion" "data_ingestion.py"
create_package "pattern-analysis" "api_handler_simple.py"  # Reuse simple handler for now
create_package "api-handler" "api_handler_simple.py"

echo "All Lambda packages created successfully!"
echo ""
echo "Next steps:"
echo "1. Navigate to infrastructure directory: cd ../infrastructure"
echo "2. Initialize Terraform: terraform init"
echo "3. Plan deployment: terraform plan"
echo "4. Deploy infrastructure: terraform apply"