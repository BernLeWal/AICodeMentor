#!/bin/python
"""
WorkflowInterpreter module  - Interpreter for Workflow instances
"""

import logging
import os
from enum import Enum
from dotenv import load_dotenv
from app.agents.agent import AIAgent
from app.agents.agent_factory import AIAgentFactory
from app.agents.prompt import Prompt
from app.agents.prompt_factory import PromptFactory
from app.workflow.activity import Activity
from app.workflow.workflow import Workflow
from app.workflow.workflow_factory import WorkflowFactory
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

    class CheckOperation(Enum):
        """Check operations enumeration"""
        EQUALS = 0
        CONTAINS = 1
        # TODO: MATCH_REGEX = 2

        def __str__(self):
            return self.name


    def __init__(self, workflow : Workflow = None):
        self.workflow : Workflow = workflow
        self.agent : AIAgent = None   # will be set from outside
        self.command_executor : CommandExecutor = None  # will be set from outside


    def run(self, workflow : Workflow)->Workflow.Status:
        """Run the workflow"""
        logger.info("RUN: %s", workflow.name)
        self.workflow = workflow
        current_activity = workflow.start

        while current_activity is not None:
            # pre-conditions
            if current_activity.hits > 3:
                logger.warning("Activity %s has been executed too many times",
                    current_activity.name)
                workflow.status = Workflow.Status.FAILED
                break
            current_activity.hits += 1

            # run the activity
            next_activity = current_activity.next
            if current_activity.kind == Activity.Kind.START:
                self.start()
            elif current_activity.kind == Activity.Kind.PROMPT:
                self.prompt(prompt_id = current_activity.expression)
            elif current_activity.kind == Activity.Kind.EXECUTE:
                self.execute(current_activity.expression)
            elif current_activity.kind == Activity.Kind.CHECK_STATUS:
                if not self.check_status(current_activity.expression):
                    next_activity = current_activity.other
            elif current_activity.kind == Activity.Kind.CHECK_RESULT:
                if not self.check_result(current_activity.expression):
                    next_activity = current_activity.other
            elif current_activity.kind == Activity.Kind.SUCCESS:
                self.success()
                break
            elif current_activity.kind == Activity.Kind.FAILED:
                self.failed()
                break

            # post-conditions
            current_activity = next_activity

        logger.info("DONE:%s with result %s", workflow.name, workflow.status)
        return workflow.status

    def start(self):
        """Start the workflow"""
        logger.info("START: %s", self.workflow.name)
        self.workflow.status = Workflow.Status.DOING


    def prompt(self,
            role : str = Prompt.USER,
            prompt_id: str = None,
            prompt_file: str = None)->None:
        """Send a prompt to the AI-agent"""
        # get the prompt content
        prompt_content = None
        if prompt_file is not None:
            prompt_content = PromptFactory.load(prompt_file)[0].content
        if prompt_id is not None:
            # handle prompt_id not found in prompts
            if prompt_id in self.workflow.prompts:
                role = self.workflow.prompts[prompt_id].role
                prompt_content = self.workflow.prompts[prompt_id].content
            else:
                logger.warning("Prompt_id {%s} not found in prompts!", prompt_id)
        if prompt_content is None:
            raise ValueError("Prompt content is not set! " + \
                f"prompt_id={prompt_id}, prompt_file={prompt_file}")

        if prompt_content.find("{{CURRENT_RESULT}}") > 0:
            prompt_content = prompt_content.replace("{{CURRENT_RESULT}}", self.workflow.result)

        if len(prompt_content) > 100:
            logger.info("PROMPT: role=%s, content=%s...",
                role, prompt_content[:100].replace("\n", "\\n"))
        else:
            logger.info("PROMPT: role=%s, content=%s",role, prompt_content)

        if self.agent is None:
            raise ValueError("AIAgent is not set")

        if Prompt.SYSTEM == role.lower():
            self.agent.system(prompt_content)
            self.workflow.result = ""
        elif Prompt.ASSISTANT == role.lower():
            self.agent.advice(None, prompt_content)
            self.workflow.result = prompt_content
        else:   #if Prompt.USER == role.lower():
            self.workflow.result = self.agent.ask(prompt_content)
        if len(self.workflow.result) > 100:
            logger.info("PROMPT: result: %s...", self.workflow.result[:100].replace("\n", "\\n"))
        else:
            logger.info("PROMPT: result: %s", self.workflow.result.replace("\n", "\\n"))


    def execute(self, command: str = None):
        """Execute the commands in the current result"""
        # if workflow.result > 100 lines the cut it
        if len(self.workflow.result) > 100:
            logger.info("EXECUTE: %s...", self.workflow.result[:100].replace("\n", "\\n"))
        else:
            logger.info("EXECUTE: %s", self.workflow.result.replace("\n", "\\n"))

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

    def check_status(self, expected_status: Workflow.Status) -> bool:
        """Check if the workflow status is as expected"""
        logger.info("CHECK_STATUS: expected: %s, current: %s",
            expected_status, self.workflow.status)
        return self.workflow.status == expected_status

    def check_result(self, expected_text: str,
        operation: CheckOperation = CheckOperation.EQUALS) -> bool:
        """Check if the result is as expected"""
        if len(self.workflow.result) > 100:
            logger.info("CHECK_RESULT: expected_text: '%s' %s in '%s'...",
                expected_text, operation, self.workflow.result[:100].replace("\n", "\\n"))
        else:
            logger.info("CHECK_RESULT: expected_text: '%s' %s in '%s'",
                expected_text, operation, self.workflow.result.replace("\n", "\\n"))
        if operation == WorkflowInterpreter.CheckOperation.CONTAINS:
            return expected_text in self.workflow.result
        else: #if operation == WorkflowInterpreter.CHECK_RESULT_EQUALS:
            return self.workflow.result.strip() == expected_text.strip()

    def success(self):
        """Finish workflow with status SUCCESS"""
        logger.info("SUCCESS result: %s", self.workflow.result)
        self.workflow.status = Workflow.Status.SUCCESS

    def failed(self):
        """Finish workflow with status FAILED"""
        logger.info("FAILED result: %s", self.workflow.result)
        self.workflow.status = Workflow.Status.FAILED


if __name__ == "__main__":
    main_workflow = WorkflowFactory.load_from_mdfile("check-toolchain.wf.md")
    main_workflow.name = "Test build toolchain"
    main_interpreter = WorkflowInterpreter()
    main_interpreter.agent = AIAgentFactory.create_agent()
    main_interpreter.command_executor = ShellCommandExecutor()

    ## hardcoded workflow implementation

    # START
    start = Activity(Activity.Kind.START, "START")
    main_workflow.start = start
    main_workflow.activities[start.name] = start

    # PROMPT: System
    prompt_system = Activity(Activity.Kind.PROMPT, "PROMPT_SYSTEM", "System")
    main_workflow.activities[prompt_system.name] = prompt_system
    start.next = prompt_system

    # PROMPT: User TestGit
    prompt_testgit = Activity(Activity.Kind.PROMPT, "PROMPT_TESTGIT", "User TestGit")
    main_workflow.activities[prompt_testgit.name] = prompt_testgit
    prompt_system.next = prompt_testgit

    # EXECUTE: ShellCommands
    execute_output = Activity(Activity.Kind.EXECUTE, "EXECUTE_OUTPUT")
    main_workflow.activities[execute_output.name] = execute_output
    prompt_testgit.next = execute_output

    # PROMPT: User CommandResults
    prompt_cmdresults = Activity(Activity.Kind.PROMPT, "PROMPT_CMDRESULTS", "User CommandResults")
    main_workflow.activities[prompt_cmdresults.name] = prompt_cmdresults
    execute_output.next = prompt_cmdresults

    # CHECK_STATUS: SUCCESS
    checkresult_success = Activity(Activity.Kind.CHECK_RESULT, "CHECK_RESULT_SUCCESS", "SUCCESS")
    main_workflow.activities[checkresult_success.name] = checkresult_success
    prompt_cmdresults.next = checkresult_success

    # PROMT: User SuccessSummary
    prompt_successsummary = Activity(
        Activity.Kind.PROMPT, "PROMPT_SUCCESS_SUMMARY", "User SuccessSummary")
    main_workflow.activities[prompt_successsummary.name] = prompt_successsummary
    checkresult_success.next = prompt_successsummary

    # SUCCESS
    success = Activity(Activity.Kind.SUCCESS, "SUCCESS")
    main_workflow.activities[success.name] = success
    prompt_successsummary.next = success

    # CHECK_STATUS: FAILED
    checkresult_failed = Activity(Activity.Kind.CHECK_RESULT, "CHECK_RESULT_FAILED", "FAILED")
    main_workflow.activities[checkresult_failed.name] = checkresult_failed
    checkresult_success.other = checkresult_failed

    # PROMT: User FailedSummary
    prompt_failedsummary = Activity(
        Activity.Kind.PROMPT, "PROMPT_FAILED_SUMMARY", "User FailedSummary")
    main_workflow.activities[prompt_failedsummary.name] = prompt_failedsummary
    checkresult_failed.next = prompt_failedsummary

    # FAILED
    failed = Activity(Activity.Kind.FAILED, "FAILED")
    main_workflow.activities[failed.name] = failed
    prompt_failedsummary.next = failed

    # PROMPT: Improve
    prompt_improve = Activity(Activity.Kind.PROMPT, "PROMPT_IMPROVE", "User Improve")
    main_workflow.activities[prompt_improve.name] = prompt_improve
    failed.other = prompt_improve
    prompt_improve.next = execute_output
    checkresult_failed.other = prompt_improve


    ## run the workflow
    main_status = main_interpreter.run(main_workflow)
    if main_status == Workflow.Status.SUCCESS:
        print(f"Workflow completed with SUCCESS, Result:\n{main_workflow.result}")
        exit(0)
    else:
        print(f"Workflow completed with FAILED, Result:\n{main_workflow.result}")
        exit(1)
