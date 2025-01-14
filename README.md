# AI SourceCode Mentor

A product to automatically analyse, feedback and grade source-code project submissions using AI agents.

AI-agents will autonomously evaluate source-code projects base on program requirements and specifications. Therefore it will generate the commands (shell, etc.) which will be executed and the output analyzed autonomously.

## TODOs
Before "official" version 0.1:
* Variables Support
* CALL activity to run sub-workflows
* Record workflow processing logs
* Write processing logs to md file
* Execute the workflow in a docker container
* Implement BIC-SAM Practice1 as workflow
* Implement main.py console app

Later:
* ShellExecutor command whitelist, blacklist, reputation mechanism

## Research Questions

1. How can I reach the next AI-autonomy level in this product.

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
