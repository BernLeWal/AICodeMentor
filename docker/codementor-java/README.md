# AI CodeMentor

This image contains the tools required for Java for AI CodeMentor supporting Java and Maven.

It additionally prepares the Maven local repo cache with: Sprint Boot 3, OpenAPI 3 and further often used libraries.
ATTENTION: if the java-project uses dynamic versions (aka "LATEST") or SNAPSHOT versions, then Maven will still reload all dependencies from remote repos.

## Pre-Requisites

- Generate your own .env file into the parent (docker/) directory, based on [../.env.sample](../.env.sample)

## Build the image

From the project root directory run the following command:
```shell
docker build -t codementor-java -f docker/codementor-java/Dockerfile .
```

