# AI CodeMentor Docker Image

This image contains the base tools for AI CodeMentor supporting the Python Tools and the Bash Commandshell.

## Pre-Requisites

- Generate your own .env file into the parent (docker/) directory, based on [../.env.sample](../.env.sample)

## Build the Docker Image

From the project root directory run the following command:
```shell
docker build -t codementor -f docker/codementor/Dockerfile .
```

## Run the Docker Container

```shell
docker run --name codementor --env-file docker/.env -p 5000:5000 codementor --server
```