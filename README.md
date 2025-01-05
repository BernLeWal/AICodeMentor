# AI SourceCode Mentor

A product to automatically analyse, feedback and grade source-code project submissions using AI agents.

AI-agents will autonomously evaluate source-code projects base on program requirements and specifications. Therefore it will generate the commands (shell, etc.) which will be executed and the output analyzed autonomously.

## Research Questions

1. How can I reach the next AI-autonomy level in this product.

## Setup

- Create and activate a virtual environment, e.g. venv
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
