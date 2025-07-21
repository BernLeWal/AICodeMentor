# Docker Images for AICodeMentor

This directory contains scripts to build the different Docker Images for AI CodeMentor.

The CodeMentor comes in different flavors, which is the execution-system which the mentor is equipped with, meaning which commands it is able to execute.

Currently there are two types of the AICodeMentor:
- **codementor** .. The runtime engine contains a container equipped with Python3.13 and support of external/cloud LLMs.
- **codementor-cuda** .. The runtime engines is based on codementor, supporting running LLMs locally. This uses Huggingface Transformer library and Nvidias CUDA library.

AICodeMentor uses external containers to execute commands, so called **shellboxes**:
- **shellbox** .. Ubuntu based bash shell
- **shellbox-java** .. Ubuntu based bash shell with Java LTS JDK and Maven build system installed

## Build the Docker Image

The application runs in a docker-container, so the docker-image has to be built beforehand.
(The run-scripts check and build it automatically)

Attention: Run the following command from the **project root directory**!

To build the codementor:
```shell
docker build -t codementor -f docker/codementor/Dockerfile .
```

Replace the image and path-files accordingly to generate the other images

## Tag the Docker Image

The list of application versions can be read from the sources, see [app/version.py](../app/version.py)

When you want to use a specific tag instead of ":latest", the use the following commands, e.g. for tag "0.2.3":

```shell
docker tag codementor codementor:0.2.3
```

To verify if tagging was ok, list the images:

```shell
docker images codementor
```


## Publish the image an the hub.docker.com registry

Remarks: replace *codepunx* with you own registry username.

```shell
docker tag codementor:latest codepunx/codementor:latest
```

When you want to use a specific tag then replace the ":latest", e.g. with "0.2.3" to tag the version 0.2.3

Then push your image into the registry

```shell
docker login
docker push codepunx/codementor:latest
```

