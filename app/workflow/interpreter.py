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
        if current_activity is None:
            current_activity = workflow.activities[Activity.Kind.START.name]

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
            elif current_activity.kind == Activity.Kind.ASSIGN:
                self.assign(current_activity.expression)
            elif current_activity.kind == Activity.Kind.PROMPT:
                self.prompt(prompt_id = current_activity.expression)
            elif current_activity.kind == Activity.Kind.EXECUTE:
                self.execute(current_activity.expression)
            elif current_activity.kind == Activity.Kind.CHECKSTATUS:
                if not self.check_status(current_activity.expression):
                    next_activity = current_activity.other
            elif current_activity.kind == Activity.Kind.CHECKRESULT:
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

    def assign(self, value: str = None)->None:
        """Assign a prompt to the result (like a "copy" operation)"""
        content = None
        if value is not None:
            # Try to use value as a prompt_id to get the content from prompts
            if value in self.workflow.prompts:
                content = self.workflow.prompts[value].content
            else:
                content = value
        if content is None:
            raise ValueError("ASSIGN Value is not set! ")
        if content.find("{{CURRENT_RESULT}}") > 0:
            content = content.replace("{{CURRENT_RESULT}}", self.workflow.result)
        if len(content) > 100:
            logger.info("ASSIGN: %s...", content[:100].replace("\n", "\\n"))
        else:
            logger.info("ASSIGN: %s", content)
        self.workflow.result = content


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
            raise ValueError("PROMPT content is not set! " + \
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
        if command is not None and len(command) > 0:
            commands = [Command(Command.SHELL, [command])]
        else:
            commands = Parser().parse(self.workflow.result)
        self.workflow.result = ""
        for cmd in commands:
            self.command_executor.execute(cmd)
            self.workflow.result += cmd.output

    def check_status(self, expected_status: Workflow.Status) -> bool:
        """Check if the workflow status is as expected"""
        logger.info("CHECKSTATUS: expected: %s, current: %s",
            expected_status, self.workflow.status)
        return self.workflow.status == expected_status

    def check_result(self, expected_text: str,
        operation: CheckOperation = CheckOperation.EQUALS) -> bool:
        """Check if the result is as expected"""
        if len(self.workflow.result) > 100:
            logger.info("CHECKRESULT: expected_text: '%s' %s in '%s'...",
                expected_text, operation, self.workflow.result[:100].replace("\n", "\\n"))
        else:
            logger.info("CHECKRESULT: expected_text: '%s' %s in '%s'",
                expected_text, operation, self.workflow.result.replace("\n", "\\n"))
        if operation == WorkflowInterpreter.CheckOperation.CONTAINS:
            return expected_text in self.workflow.result
        else: #if operation == WorkflowInterpreter.CHECKRESULT_EQUALS:
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
