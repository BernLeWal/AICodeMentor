#!/bin/bash

# Make sure the script is executable
# Usage: ./run_codementor.sh [additional arguments for your application]

# Image name
IMAGE_NAME="codementor-java"

# Check if the image exists, build it if not
if ! docker images | grep -q $IMAGE_NAME; then
    echo "Docker image not found. Building the image..."
    docker build -t $IMAGE_NAME -f docker/codementor-java/Dockerfile .
fi

# Run the container with the given arguments
docker run --rm \
    --env-file docker/.env \
    -v "$(pwd)/workflows:/home/mentor/workflows" \
    -v "$(pwd)/log:/home/mentor/log" \
    -p 5000:5000 \
    $IMAGE_NAME "$@"
