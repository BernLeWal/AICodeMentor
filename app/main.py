#!/bin/python
"""
AI CodeMentor
automatically analyse, feedback and grade source-code project submissions using AI agents
"""
import logging
import sys
import os
import argparse
from dotenv import load_dotenv

from app.version import __version__, __app_name__, __app_description__
from app.agents.agent_factory import AIAgentFactory
from app.agents.agent_config import AIAgentConfig
from app.workflow.workflow_reader import WorkflowReader
from app.workflow.interpreter import WorkflowInterpreter
from app.workflow.workflow import Workflow
from app.workflow.context import Context
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


def show_help() -> None:
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


def run(workflow_file, key_values) -> tuple[Workflow.Status, str]:
    """Run the AI CodeMentor application
    :param workflow_file: Path to the workflow file in Markdown format
    :return: Exit code
    """
    main_workflow = WorkflowReader().load_from_mdfile(workflow_file, ".")
    print(f"Running workflow: {main_workflow.name} (from file {main_workflow.filepath}) "+\
          f"using AI-model {AIAgentConfig.get_model_name()} ")
    if key_values:
        print("with parameters:")
        for kv in key_values:
            key, value = kv.split("=")
            print(f"  - {key}={value}\n")
            main_workflow.params[key] = value

    main_interpreter = WorkflowInterpreter(main_workflow)

    ## run the workflow
    main_context = Context(main_workflow, AIAgentFactory.create_agent(), ShellCommandExecutor())
    return main_interpreter.run(main_context)



if __name__ == "__main__":
    # For debugging, uncomment and set the following lines
    #sys.argv.append("--verbose")
    #sys.argv.append("workflows/sample-project-eval.wf.md")
    #sys.argv.append("REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git")

    parser = argparse.ArgumentParser(
        description=f"{__app_name__} - {__app_description__}"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{__app_name__} V{__version__}",
        help="Show program's version number and exit"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Write the log-output also to the console"
    )
    parser.add_argument(
        '-s', '--server',
        action='store_true',
        help="Run the application as a server"
    )
    parser.add_argument(
        'workflow_file',
        metavar='<workflow-file.md>',
        type=str,
        help="Path to the workflow file in Markdown format"
    )
    parser.add_argument(
        'key_values',
        metavar='<key=value>',
        type=str,
        nargs='*',
        help="Optional key-value pairs to pass to the application"
    )

    args = parser.parse_args()
    if args.verbose or args.server:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    if args.server:
        #from app.server import run_server
        #run_server()
        sys.exit(0)

    (main_status, main_result) = run(args.workflow_file, args.key_values)
    if main_status == Workflow.Status.SUCCESS:
        print(f"Workflow completed with SUCCESS\n\n---\n{main_result}")
        sys.exit(0)
    else:
        print(f"Workflow completed with FAILED\n\n---\n{main_result}")
        sys.exit(1)
