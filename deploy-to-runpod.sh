#!/bin/bash

# Configuration
DOCKER_USERNAME="yurui666"
IMAGE_NAME="pdf-dashboard"
TAG="latest"
FULL_IMAGE_NAME="$DOCKER_USERNAME/$IMAGE_NAME:$TAG"

echo "🚀 Starting deployment to RunPod..."

# 1. Build the Docker image
echo "📦 Building Docker image..."
docker build -t $FULL_IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# 2. Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push $FULL_IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed!"
    exit 1
fi

echo "✅ Image successfully pushed to Docker Hub: $FULL_IMAGE_NAME"
echo ""
echo "🎯 Next steps for RunPod deployment:"
echo "1. Go to https://runpod.io/console/pods"
echo "2. Click 'Deploy'"
echo "3. Select 'Community Cloud' or 'Secure Cloud'"
echo "4. Choose 'Deploy from Docker Image'"
echo "5. Enter: $FULL_IMAGE_NAME"
echo "6. Configure the following:"
echo "   - Port: 8501"
echo "   - Environment variables (if needed):"
echo "     - PDF_DIR=/workspace/data/gotriple_pdfs"
echo "     - MARKDOWN_DIR=/workspace/data/extracted"
echo "     - PAGE_SCORES_CSV=/workspace/data/page_scores_full.csv"
echo "     - METADATA_PKL=/workspace/data/metadata_openalex(silver).pkl"
echo "7. Deploy!"
echo ""
echo "🔗 Your dashboard will be available at: https://your-pod-id.proxy.runpod.net" 