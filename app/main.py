#!/bin/python
"""
AI CodeMentor
automatically analyse, feedback and grade source-code project submissions using AI agents
"""
import logging
import sys
import os
from dotenv import load_dotenv

from app.agents.agent_factory import AIAgentFactory
from app.workflow.workflow_reader import WorkflowReader
from app.workflow.interpreter import WorkflowInterpreter
from app.workflow.workflow import Workflow
from app.commands.shell_executor import ShellCommandExecutor

# Setup logging framework
load_dotenv()
logfiles_dir = os.getenv('LOGFILES_DIR', './logs')
os.makedirs(logfiles_dir, exist_ok=True)
logfile_path = os.path.join(logfiles_dir, 'codementor.log')
if logging.getLogger().hasHandlers():
    logging.getLogger().handlers.clear()    #remove existing default handlers
logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                    format=os.getenv('LOGFORMAT', 'pretty'),
                    handlers=[
                        logging.FileHandler(logfile_path),
                        #logging.StreamHandler(sys.stdout)  # Optional: to also log to console
                    ])
logger = logging.getLogger(__name__)


def show_help():
    """Show help"""
    print("AI CodeMentor - automatically analyse, feedback and grade " +\
        "source-code project submissions using AI agents")
    print()
    print("Usage: python main.py [options] <workflow-file.md> [key=value ...]")
    print()
    print("Options:")
    print("  -h, --help         Show this help message and exit")
    print()
    print("Example:")
    print("  python main.py workflow.md FOO1=BAR1 FOO2=BAR2")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        exit(1)
        #sys.argv.append("workflows/bif5-swkom/paperless-sprint1.wf.md")
        #sys.argv.append("REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git")

    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        show_help()
        exit(0)

    main_workflow = WorkflowReader.load_from_mdfile(sys.argv[1], ".")
    print(f"Running workflow: {main_workflow.name} (from file {main_workflow.filepath})  ")
    if len(sys.argv) > 2:
        print("with parameters:  ")
        for arg in sys.argv[2:]:
            key, value = arg.split("=")
            print(f"  - {key}={value}\n")
            main_workflow.variables[key] = value
        print("\n")
    main_interpreter = WorkflowInterpreter()
    main_interpreter.agent = AIAgentFactory.create_agent()
    main_interpreter.command_executor = ShellCommandExecutor()

    ## run the workflow
    main_status = main_interpreter.run(main_workflow)
    if main_status == Workflow.Status.SUCCESS:
        print(f"Workflow completed with SUCCESS\n\n---\n{main_workflow.result}")
        exit(0)
    else:
        print(f"Workflow completed with FAILED\n\n---\n{main_workflow.result}")
        exit(1)
