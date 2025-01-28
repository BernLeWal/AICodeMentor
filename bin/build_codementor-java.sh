#!/bin/bash

# Make sure the script is executable
# Usage: ./build_codementor-java.sh

docker build -t codementor-java -f docker/codementor-java/Dockerfile .