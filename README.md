# AI Code Mentor

A **runtime** on which to build applications with integrated autonomous AI-agents. The applications are defined as workflows, which are written together with prompts in Markdown files (.wf.md) which will be interpreted by the CodeMentor.

The **AI-agents** (mutliple instances are provided) will generate commands (bash shell commands, etc.), which will be executed directly and the output fed back to the AI-agents to make them analyze the outcome of their tasks. A feature is, that the AI-agents may iterate over their tasks to improve the results when necessary. Currently Platform OpenAI is integrated, but in future there will be added alternatives.

A provided **sample scenario: automatic grading of software-development assignments** is a workflow to automatically analyse, feedback and grade source-code project submissions using AI agents (the author comes from the software development education area): AI-agents will autonomously evaluate source-code projects base on program requirements and specifications. 

Added benefits/differences to use ChatGPT:
- The **data working on is staying local** (and not uploaded into the cloud completely), and is worked with inside the docker container. AI is used with Prompts to generate commands which work on the data locally.
- The **commands the AI suggests are excecuted automatically** in the local container, so there is no manual copy&paste of text between the chat window and your machine. 
- ChatGPT **Canvas is still limited**, it can execute commands also, but will do that in the cloud and is limited (currently) when it comes to deal with multiple files and complex execution environments.
- **Multiple AI-agents** run on the same workflow at the same time, separating the tasks and individual task-goals.
- AI needs good context to better fulfil its tasks, with the **workflows** the goal and way to achieve it is defined much more clear compared to only text prompts. Especially paths, branches and alternative ways can be modelled.
- CodeMentor allows to easily **automate and scale** for using the same workflow on multiple targets, e.g. run the same workflow not only of one sourcecode-submission (the sample scenario above), but for 100.
- **Traceability** allows to analyse which prompts and which commands are executed with which result in a step-by-step manner. This opens up the "black box" to see what is really happening inside the runtime.

Screenshots of the running application:
- Part of the defined workflow (here for REST-Service function evaluation):

![](./docs/Screenshot_run_workflow.png)

- Console output with the result of the CodeMentor run

![](./docs/screenshot_run_console_output.png)

## Implementation Status

### TODOs
Before "official" version 0.1 (the MVP):
* Write workflow for https://github.com/BernLeWal/fhtw-bif5-swkom-paperless
    * sub-workflow for command-prompts supporting step-by-step and AI-Agent improvements

Later:
* Record a video "shorts" about the idea and product --> for LinkedIn, YouTube
* ShellExecutor command whitelist, blacklist, reputation mechanism
* feedback for the AIAgent on the prompt results for improvement (learning)
* AIAgent collaboration sequence diagram written
* Add Activity to ask user for input
* --server mode with REST API (to avoid volume-mounts)

### Research Questions

1. Q: How can I reach the next AI-autonomy level in this product.  
   A: Fulfil all aspects of the AI-Agent definition published by Google in their paper about [*Agents*](https://media.licdn.com/dms/document/media/v2/D561FAQH8tt1cvunj0w/feedshare-document-pdf-analyzed/B56ZQq.TtsG8AY-/0/1735887787265?e=1736985600&v=beta&t=pLuArcKyUcxE9B1Her1QWfMHF_UxZL9Q-Y0JTDuSn38)

    - Connected to external systems
    - Managed session with multi-turn inference between the "system" and the "agent"
    - Tools are natively implemented in the agent Architecture
    - Agent learns by the feedback it gets itself by the "system"

2. Q: How does software-development differ when dealing with AI-agents vs. the classical approach  
   A: Classical- --vs-- AI-included Programming:  
    - The output and behavior of AI-Agents is not so deterministic as with formal programming.
    - E.g. there is no "grammar" to parse AI-Agent output; parsers have to be implemented to be more error-prone (which is up to creativity and intuition of the programmer)
    - a better approach would be for the parser to ask the AIAgent to improve the output


## Usage

### Pre-Requisites

- Docker environment (see https://www.docker.com/products/docker-desktop/)
- Ensure that the shell-scripts have execution rights ```chmod a+x *.sh```

### Running

Run the AI CodeMentor using the prepared shell scripts:
- On Linux: ```bin/run_codementor.sh [options] <workflow-file.md> [<key=value> ...]```
- On Windows: ```bin/run_codementor.ps1 [options] <workflow-file.md> [<key=value> ...]```
see [bin/README.md](./bin/README.md) for details.

Options:
- ```-h```, ```--help```         Show this help message and exit
- ```-v```, ```--version```      Show application version
- ```-verbose```                 Display application log also in console

Arguments:
- *<workflow-file.md>*    A Markdown file containing the definition of the workflow and prompts, see [workflows/check-toolchain.wf.md](workflows/check-toolchain.wf.md) for an example
- *[<key=value> ...]*   Parameters to be sent to the workflow. Multiple key/value pairs are allowed.

### Example

To run the workflow [check-toolchain.wf.md](workflows/check-toolchain.wf.md) with a specific REPO_URL [https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git](https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git) as parameter.

Linux:
```bash
$ bin/run_codementor-java.sh workflows/check-toolchain.wf.md REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git
```

Windows:
```powershell
PS > bin\run_codementor-java.ps1 workflows/check-toolchain.wf.md REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git
```

ATTENTION: You must use the normal slash '/' is path parameters, because the app is running in a linux environment.

### Logging

The console (stdin/stout/stderr) is used by the CLI interface of the application, 
so logs are written to the file [log/codementor.log](log/codementor.log) instead - and not to console.
Unfortunately this means, that the docker log will stay empty as long as not running with "--verbose" or in server ("--server") mode.

---

## Development

### Setup

- Install Python3 (>3.12), and pip3
    ```shell
    sudo apt install python3 python3-pip -y
    ```
- Create and activate a virtual environment, e.g. venv
    ```shell
    #sudo apt install python3-venv -y
    pip install virtualenv
    python -m virtualenv .venv
    source .venv/bin/activate
    ```
- Install required libraries:
    ```shell
    pip install -r requirements.txt
    ```

### Running/Debugging

- Ensure that the PYTHONPATH is set when you want to run the Python files directly, e.g.
    - BASH:
    ```sh
    export PYTHONPATH=$(pwd)
    ```
    - Windows (PowerShell):
    ```powershell
    $env:PYTHONPATH = (Get-Location).Path
    ```

- Run the console app providing a workflow Markdown file
    ```sh
    python app/main.py workflows/check-toolchain.wf.md
    ```

    The usage of the tool is as follows:
    ```sh
    $ python app/main.py -h
    AI CodeMentor - automatically analyse, feedback and grade source-code project submissions using AI agents

    Usage: python main.py [options] <workflow-file.md> [key=value ...]

    Options:
        -h, --help         Show this help message and exit

    Example:
        python main.py workflow.md FOO1=BAR1 FOO2=BAR2
    ```

- Run the console app to evaluate a sample project
    ```sh
    python app/main.py workflows/swkom/paperless-sprint1.wf.md REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git
    ```

## Documentation

Software Architecture and Implementation Documentation see [docs/README.md](./docs/README.md)
