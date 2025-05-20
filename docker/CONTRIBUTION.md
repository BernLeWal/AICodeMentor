# Docker Images for AICodeMentor

This directory contains scripts to build the different Docker Images for AI CodeMentor.

The CodeMentor comes in different flavors, which is the execution-system which the mentor is equipped with, meaning which commands it is able to execute.

Currently there are two types:
- **codementor** .. The runtime engine contains a container equipped with Python3.12 and BASH (-slim)
- **codementor-java** .. The runtime engines is based on codementor, with Java JDK and Maven built system added.


## Build the Docker Image

The application runs in a docker-container, so the docker-image has to be built beforehand.
(The run-scripts check and build it automatically)

Attention: Run the following command from the **project root directory**!

To build the codementor:
```shell
docker build -t codementor -f docker/codementor/Dockerfile .
```

To build the codementor-java:
```shell
docker build -t codementor-java -f docker/codementor-java/Dockerfile .
```

## Tag the Docker Image

The list of application versions can be read from the sources, see [app/version.py](../app/version.py)

When you want to use a specific tag instead of ":latest", the use the following commands, e.g. for tag "0.1.6":

```shell
docker tag codementor codementor:0.1.6
```

To verify if tagging was ok, list the images:

```shell
docker images codementor
```


## Publish the image an the hub.docker.com registry

Remarks: replace <yourusername> with you own registry username.

```shell
docker tag codementor:latest <yourusername>/codementor:latest
```

When you want to use a specific tag then replace the ":latest", e.g. with "0.1.6" to tag the version 0.1.6

Then push your image into the registry

```shell
docker login
docker push <yourusername>/codementor:latest
```

