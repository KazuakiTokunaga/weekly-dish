#!/bin/bash

# Load environment variables from .env file
source .env

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID is not set. Please define it in the .env file."
  exit 1
fi

# Build
docker build --no-cache=true --platform linux/x86_64 -f Dockerfile . -t "asia-northeast1-docker.pkg.dev/$PROJECT_ID/recipe/recipe-app:dev"

# Push
docker push asia-northeast1-docker.pkg.dev/$PROJECT_ID/recipe/recipe-app:dev

# Deploy
gcloud run deploy recipe-service-app \
  --project "$PROJECT_ID" \
  --image asia-northeast1-docker.pkg.dev/$PROJECT_ID/recipe/recipe-app:dev \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated
