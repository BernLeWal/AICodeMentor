# AI CodeMentor Scripts

This directory contains shell scripts to build and execute the AI CodeMentor. There are versions for linux BASH (*.sh) and Windows PowerShell (*.ps1)

The CodeMentor comes in different flavors, which is the execution-system which the mentor is equipped with, meaning which commands it is able to execute.

Currently there are two types:
- **codementor** .. The runtime engine contains a container equipped with Python3.12 and BASH (-slim)
- **codementor-java** .. The runtime engines is based on codementor, with Java JDK and Maven built system added.


## Pre-Requisites

- Ensure that the shell-scripts have execution rights ```chmod a+x *.sh```

- To shorten the command-line, you may set a symbolic link to the execution engine of your choice, f.e. ```ln -s run_codementor-java.sh run.sh```

## Usage

### Build the application

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

### Run the application

Run the AI CodeMentor using the prepared shell scripts:
- On Linux: ```bin/run_codementor.sh [options] <workflow-file.md> [<key=value> ...]```
- On Windows: ```bin/run_codementor.ps1 [options] <workflow-file.md> [<key=value> ...]```

### Publish the image an the hub.docker.com registry

When you want to use a specific tag instead of ":latest", the use the following commands, e.g. for tag "0.1.6":

Remarks: replace <yourusername> with you own registry username.

```shell
docker tag codementor codementor:0.1.6
docker tag codementor:0.1.6 <yourusername>/codementor:0.1.6
```

Then push your image into the registry

```shell
docker login
docker tag codementor:0.1.6 <yourusername>/codementor:0.1.6
```
