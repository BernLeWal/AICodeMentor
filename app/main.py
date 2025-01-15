#!/bin/python
"""
AI CodeMentor - automatically analyse, feedback and grade source-code project submissions using AI agents
"""
import logging
import sys

from app.agents.agent_factory import AIAgentFactory
from app.workflow.workflow_factory import WorkflowFactory
from app.workflow.interpreter import WorkflowInterpreter
from app.workflow.workflow import Workflow
from app.commands.shell_executor import ShellCommandExecutor

# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def show_help():
    """Show help"""
    print("AI CodeMentor - automatically analyse, feedback and grade " +\
        "source-code project submissions using AI agents")
    print()
    print("Usage: python main.py [options] <workflow-file.md>")
    print()
    print("Options:")
    print("  -h, --help         Show this help message and exit")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        exit(1)

    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        show_help()
        exit(0)

    main_workflow = WorkflowFactory.load_from_mdfile(sys.argv[1], ".")
    main_interpreter = WorkflowInterpreter()
    main_interpreter.agent = AIAgentFactory.create_agent()
    main_interpreter.command_executor = ShellCommandExecutor()

    ## run the workflow
    main_status = main_interpreter.run(main_workflow)
    if main_status == Workflow.Status.SUCCESS:
        print(f"Workflow completed with SUCCESS, Result:\n{main_workflow.result}")
        exit(0)
    else:
        print(f"Workflow completed with FAILED, Result:\n{main_workflow.result}")
        exit(1)
