#!/bin/python
"""
WorkflowInterpreter module  - Interpreter for Workflow instances
"""

import logging
import os
from dotenv import load_dotenv
from app.agents.agent import AIAgent
from app.agents.agent_factory import AIAgentFactory
from app.agents.prompt import Prompt
from app.agents.prompt_factory import PromptFactory
from app.workflow.workflow import Workflow
from app.commands.command import Command
from app.commands.parser import Parser
from app.commands.executor import CommandExecutor
from app.commands.shell_executor import ShellCommandExecutor


# Setup logging framework
load_dotenv()
logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                    format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


class WorkflowInterpreter:
    """The base class for all WorkflowInterpreter implementations"""

    CHECK_RESULT_EQUALS = 0
    CHECK_RESULT_CONTAINS = 1
    #CHECK_RESULT_MATCH_REGEX = 2


    def __init__(self, workflow: Workflow):
        self.workflow : Workflow = workflow
        self.agent : AIAgent = None   # will be created on demand
        self.command_executor : CommandExecutor = None  # will be set from outside
        logger.debug("WorkflowInterpreter initialized with workflow: %s",
            self.workflow.name)


    def start(self):
        """Start the workflow"""
        logger.info("Starting workflow: %s", self.workflow.name)
        self.workflow.status = Workflow.DOING


    def prompt(self,
            role : str = Prompt.USER,
            prompt_id: str = None,
            prompt_file: str = None,
            append_results: bool = False)->None:
        """Send a prompt to the AI-agent"""
        logger.info("Prompting with role=%s, prompt_id=%s, prompt_file=%s",
                role, prompt_id, prompt_file)
        if self.agent is None:
            self.agent = AIAgentFactory.create_agent()
        if prompt_file is not None:
            prompt_content = PromptFactory.load(prompt_file)[0].content
        else:
            raise ValueError("prompt_file is required")
        if append_results:
            prompt_content += self.workflow.result

        if Prompt.SYSTEM == role.lower():
            self.agent.system(prompt_content)
            self.workflow.result = ""
        else:   #if Prompt.USER == role.lower():
            self.workflow.result = self.agent.ask(prompt_content)


    def execute(self, command: str = None):
        """Execute the commands in the current result"""
        logger.info("Executing commands of: %s", self.workflow.result)
        if self.command_executor is None:
            raise ValueError("CommandExecutor is not set")
        if command is not None:
            commands = [Command(Command.SHELL, [command])]
        else:
            commands = Parser().parse(self.workflow.result)
        self.workflow.result = ""
        for cmd in commands:
            self.command_executor.execute(cmd)
            self.workflow.result += cmd.output

    def check_status(self, expected_status: int) -> bool:
        """Check if the workflow status is as expected"""
        logger.debug("Checking status. Expected: %d, Current: %d",
            expected_status, self.workflow.status)
        return self.workflow.status == expected_status

    def check_result(self, expected_text: str, operation: int = CHECK_RESULT_EQUALS) -> bool:
        """Check if the result is as expected"""
        logger.debug("Checking result with expected text: %s and operation: %d",
            expected_text, operation)
        if operation == WorkflowInterpreter.CHECK_RESULT_CONTAINS:
            return expected_text in self.workflow.result
        else: #if operation == WorkflowInterpreter.CHECK_RESULT_EQUALS:
            return self.workflow.result.strip() == expected_text.strip()

    def success(self):
        """Finish workflow with status SUCCESS"""
        logger.info("Finished workflow with status SUCCESS")
        self.workflow.status = Workflow.SUCCESS

    def failed(self):
        """Finish workflow with status FAILED"""
        logger.info("Finished workflow with status FAILED")
        self.workflow.status = Workflow.FAILED


if __name__ == "__main__":
    main_workflow = Workflow(name="Test build toolchain")
    main_interpreter = WorkflowInterpreter(main_workflow)
    main_interpreter.command_executor = ShellCommandExecutor(ShellCommandExecutor.SHELL_CMD)

    ## hardcoded workflow implementation
    # START
    main_interpreter.start()  # no input required

    # PROMPT: System
    main_interpreter.prompt(
        Prompt.SYSTEM,
        prompt_file="prep-agent.system.prompt.md")

    # PROMPT: User TestGit
    main_interpreter.prompt(
        Prompt.USER,
        prompt_file="prep-agent.test-git.prompt.md")

    iteration = 1
    while iteration < 3:

        # EXECUTE: ShellCommands
        main_interpreter.execute()

        # PROMPT: User CommandResults
        main_interpreter.prompt(
            Prompt.USER,
            prompt_file="prep-agent.test-git-results.prompt.md",
            append_results=True)

        # CHECK_STATUS: SUCCESS
        if main_interpreter.check_result("SUCCESS"):

            # PROMT: User SuccessSummary
            main_interpreter.prompt(
                Prompt.USER,
                prompt_file="prep-agent.test-git-success.prompt.md")

            # SUCCESS
            main_interpreter.success()
            print(main_interpreter.workflow.result)
            exit(0)

        if main_interpreter.check_result("FAILED"):

            # PROMT: User FailedSummary
            main_interpreter.prompt(
                Prompt.USER,
                prompt_file="prep-agent.test-git-failed.prompt.md")

            # FAILED
            main_interpreter.failed()
            print(main_interpreter.workflow.result)
            exit(1)

        # PROMPT: Improve
        main_interpreter.prompt(
            Prompt.USER,
            prompt_file="prep-agent.test-git-improve.prompt.md")
        iteration += 1

    # FAILED: no solution found
    print("No solution found")
    exit(2)
