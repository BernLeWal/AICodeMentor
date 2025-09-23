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
from app.agents.agent_config import AIAgentConfig
from app.workflow.batch_config import BatchConfig
from app.workflow.batch_runner import BatchRunner
from app.workflow.workflow import Workflow
from app.workflow.workflow_runner import WorkflowRunner

# Setup logging framework
load_dotenv()
logfiles_dir = os.getenv('LOGFILES_DIR', './log')
os.makedirs(logfiles_dir, exist_ok=True)
logfile_path = os.path.join(logfiles_dir, 'codementor.log')

# Always clear all handlers before configuring logging
root_logger = logging.getLogger()
if root_logger.hasHandlers():
    root_logger.handlers.clear()

logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                    format=os.getenv('LOGFORMAT', '%(message)s'),
                    handlers=[
                        logging.FileHandler(logfile_path),
                        #logging.StreamHandler(sys.stdout)  # Optional: to also log to console
                    ])
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # For debugging, uncomment and set the following lines:
    #sys.argv.append("--help")

    # Scenario 1: workflow execution
    #sys.argv.append("--verbose")
    #sys.argv.append("workflows/tutorial/lesson1.wf.md")

    #sys.argv.append("--verbose")
    #sys.argv.append("workflows/sample-project-eval.wf.md")
    #sys.argv.append("REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git")

    # Scenario 2: batch execution
    #sys.argv.append("--batch")
    #sys.argv.append("workflows/benchmarks/summarize-sourcefile.cfg.json")
    #sys.argv.append("workflows/source-eval/sam-rest.cfg.json")

    # Scenario 3: run as server
    #sys.argv.append("--server")

    parser = argparse.ArgumentParser(
        description=f"{__app_name__} - {__app_description__}"
    )
    parser.add_argument(
        "--version", "-v",
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
        '--server', '-s',
        action='store_true',
        help="Run the application as a server"
    )
    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help="Run the application in batch mode"
    )
    parser.add_argument(
        'workflow_file',
        metavar='<workflow-file.md|batch-config.json>',
        type=str,
        nargs='?',
        help="Path to the workflow file (in Markdown format) "+\
            "or batch configuration file (in JSON format)"
    )
    parser.add_argument(
        'key_values',
        metavar='<key=value>',
        type=str,
        nargs='*',
        help="Optional key-value pairs to pass to the application"
    )

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    elif args.server:
        # clear all handlers, and add only a StreamHandler to log to stdout
        # otherwise Flask will not log to the console
        if logging.getLogger().hasHandlers():
            logging.getLogger().handlers.clear()
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logger.info("Running in server mode, logging to console")


    if args.server:
        # run the application as a RESTful server
        from server import AICodeMentorServer
        server = AICodeMentorServer()
        server.run()
    else:
        # normal run and exit after execution

        if args.workflow_file is None:
            print("Error: No workflow-file or batch.-config specified")
            sys.exit(1)

        if args.batch:
            batch_cfg = BatchConfig.from_json_file(args.workflow_file)
            BatchRunner(batch_cfg).run()
            sys.exit(0)

        # else normal workflow execution
        key_values_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in args.key_values} if args.key_values else None
        runner = WorkflowRunner(args.workflow_file, key_values_dict)
        (main_status, main_result) = runner.run()
        if main_status == Workflow.Status.SUCCESS:
            print(f"Workflow completed with SUCCESS\n\n---\n{main_result}")
            sys.exit(0)
        else:
            print(f"Workflow completed with FAILED\n\n---\n{main_result}")
            sys.exit(1)
