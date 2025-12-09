#!/bin/bash

echo "=============================="
echo " Docker Automation Script"
echo "=============================="

# -----------------------------
# Ask Dockerfile name
# -----------------------------
read -p "Enter Dockerfile name (default: Dockerfile): " DOCKERFILE
DOCKERFILE=${DOCKERFILE:-Dockerfile}

if [ ! -f "$DOCKERFILE" ]; then
  echo "❌ Dockerfile '$DOCKERFILE' not found. Exiting."
  exit 1
fi

# -----------------------------
# Image name
# -----------------------------
read -p "Enter image name to build: " IMAGE_NAME
if [ -z "$IMAGE_NAME" ]; then
  echo "❌ Image name cannot be empty. Exiting."
  exit 1
fi

echo "✅ Building Docker image..."
docker build -f "$DOCKERFILE" -t "$IMAGE_NAME" . || exit 1

# -----------------------------
# Push to Docker Hub?
# -----------------------------
read -p "Do you want to push image to Docker Hub? (yes/no): " PUSH_CHOICE
if [[ "$PUSH_CHOICE" == "yes" ]]; then

  read -p "Enter Docker Hub username: " DOCKER_USER
  if [ -z "$DOCKER_USER" ]; then
    echo "❌ Docker Hub username required. Exiting."
    exit 1
  fi

  FULL_IMAGE="$DOCKER_USER/$IMAGE_NAME:latest"

  echo "✅ Logging in to Docker Hub..."
  docker login || exit 1

  echo "✅ Tagging image..."
  docker tag "$IMAGE_NAME" "$FULL_IMAGE" || exit 1

  echo "✅ Pushing image to Docker Hub..."
  docker push "$FULL_IMAGE" || exit 1

  echo "✅ Image pushed: $FULL_IMAGE"
else
  echo "⏭ Skipping Docker push."
fi

# -----------------------------
# Run container?
# -----------------------------
read -p "Do you want to run the container now? (yes/no): " RUN_CHOICE
if [[ "$RUN_CHOICE" == "yes" ]]; then

  read -p "Enter port to expose (host:container) [example 5000:5000]: " PORT_MAP
  read -p "Do you want to pass GROQ_API_KEY via .env file? (yes/no): " ENV_CHOICE

  if [[ "$ENV_CHOICE" == "yes" ]]; then
    if [ ! -f ".env" ]; then
      echo "❌ .env file not found. Exiting."
      exit 1
    fi
    docker run -it --env-file .env -p "$PORT_MAP" "$IMAGE_NAME"
  else
    read -p "Enter GROQ_API_KEY: " GROQ_API_KEY
    docker run -it -e GROQ_API_KEY="$GROQ_API_KEY" -p "$PORT_MAP" "$IMAGE_NAME"
  fi

else
  echo "✅ Done. Exiting without running container."
  exit 0
fi
