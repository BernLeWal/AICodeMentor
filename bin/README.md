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
- On Linux: ```bin/build_codementor.sh```
- On Windows: ```bin/build_codementor.ps1```

### Run the application

Run the AI CodeMentor using the prepared shell scripts:
- On Linux: ```bin/run_codementor.sh [options] <workflow-file.md> [<key=value> ...]```
- On Windows: ```bin/run_codementor.ps1 [options] <workflow-file.md> [<key=value> ...]```
