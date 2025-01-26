# AI CodeMentor Docker Image

This image contains the base tools for AI CodeMentor supporting the Python Tools and the Bash Commandshell.

## Pre-Requisites

- Generate your own .env file into the current directory, based on [../../.env.sample](../../.env.sample)

## Build the image

From the project root directory run the following command:
```shell
docker build -t codementor -f docker/codementor/Dockerfile .
```

