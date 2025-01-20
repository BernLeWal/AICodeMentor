# AI SourceCode Mentor

A product to automatically analyse, feedback and grade source-code project submissions using AI agents.

AI-agents will autonomously evaluate source-code projects base on program requirements and specifications. Therefore it will generate the commands (shell, etc.) which will be executed and the output analyzed autonomously.

## TODOs
Before "official" version 0.1 (the MVP):
* Write workflow for https://github.com/BernLeWal/fhtw-bif5-swkom-paperless
* Execute the workflow in a docker container

Later:
* ShellExecutor command whitelist, blacklist, reputation mechanism
* feedback for the AIAgent on the prompt results for improvement (learning)
* AIAgent collaboration sequence diagram written
* Add Activity to ask user for input

## Research Questions

1. Q: How can I reach the next AI-autonomy level in this product.  
   A: Fulfil all aspects of the AI-Agent definition published by Google in their paper about [*Agents*](https://media.licdn.com/dms/document/media/v2/D561FAQH8tt1cvunj0w/feedshare-document-pdf-analyzed/B56ZQq.TtsG8AY-/0/1735887787265?e=1736985600&v=beta&t=pLuArcKyUcxE9B1Her1QWfMHF_UxZL9Q-Y0JTDuSn38)

    - Connected to external systems
    - Managed session with multi-turn inference between the "system" and the "agent"
    - Tools are natively implemented in the agent Architecture
    - Agent learns by the feedback it gets itself by the "system"


## Setup

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

## Running

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
    python app/main.py workflows/bif5-swkom/paperless-sprint1.wf.md REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git
    ```

## Documentation

Software Architecture and Implementation Documentation see [docs/README.md](./docs/README.md)
