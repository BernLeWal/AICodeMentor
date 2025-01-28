#!/bin/bash

# Make sure the script is executable
# Usage: ./build_codementor.sh

docker build -t codementor -f docker/codementor/Dockerfile .