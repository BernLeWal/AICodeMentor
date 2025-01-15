#!/bin/python
"""
WorkflowInterpreter module  - Interpreter for Workflow instances
"""

import logging
import os
import re
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


    class InternalVariable(Enum):
        """Internal variables enumeration"""
        STATUS = 0
        RESULT = 1

        def __str__(self):
            return self.name

    class CheckOperation(Enum):
        """Check operations enumeration"""
        EQUALS = 0
        CONTAINS = 1
        MATCHES = 2   # regex match

        def __str__(self):
            return self.name


    def __init__(self, workflow : Workflow = None):
        self.workflow : Workflow = workflow
        self.agent : AIAgent = None   # will be set from outside
        self.command_executor : CommandExecutor = None  # will be set from outside
        self.max_hits = 3


    def run(self, workflow : Workflow)->Workflow.Status:
        """Run the workflow"""
        logger.info("RUN: %s", workflow.name)
        self.workflow = workflow
        current_activity = workflow.start
        if current_activity is None:
            current_activity = workflow.activities[Activity.Kind.START.name]

        while current_activity is not None:
            # pre-conditions
            if current_activity.hits > self.max_hits:
                self.failed( f"Activity {current_activity.name} has been executed too many times")
                break
            current_activity.hits += 1

            # run the activity
            try:
                next_activity = current_activity.next
                if current_activity.kind == Activity.Kind.START:
                    self.start()
                elif current_activity.kind == Activity.Kind.ASSIGN:
                    self.assign(current_activity.expression)
                elif current_activity.kind == Activity.Kind.SET:
                    self.set(current_activity.expression)
                elif current_activity.kind == Activity.Kind.PROMPT:
                    self.prompt(prompt_id = current_activity.expression)
                elif current_activity.kind == Activity.Kind.EXECUTE:
                    self.execute(current_activity.expression)
                elif current_activity.kind == Activity.Kind.CHECK:
                    if not self.check(current_activity.expression):
                        next_activity = current_activity.other
                        if next_activity is None:
                            self.failed()
                            break
                elif current_activity.kind == Activity.Kind.SUCCESS:
                    self.success()
                    break
                elif current_activity.kind == Activity.Kind.FAILED:
                    self.failed()
                    break
            except Exception as e:
                self.failed(str(e))
                break

            # post-conditions
            current_activity = next_activity
            if current_activity is None:
                self.success()
                break

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
            content = self.get_value(value)
        if content is None:
            raise ValueError("ASSIGN Value is not set! ")
        content = self._render_content(content)
        logger.info("ASSIGN: %s", WorkflowInterpreter.limit_str(content))
        self.workflow.result = content


    def set(self, expression: str = None)->None:
        """Set a variable value"""
        # parse the expression
        parts = str.split(expression, "=")
        if len(parts) < 2:
            raise ValueError(f"SET expression={expression} is not valid! " +\
                "Syntax: <variable>=<value>")

        name = parts[0]
        value = " ".join(parts[1:])
        value = self.get_value(value, value)
        value = self._render_content(value)
        self.set_value(name, value)
        logger.info("SET: %s='%s'", name, WorkflowInterpreter.limit_str(value))


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
            prompt_content = self.get_value(prompt_id)
            if prompt_id == "System":
                role = Prompt.SYSTEM
            elif prompt_id.startswith("Assistant "):
                role = Prompt.ASSISTANT

        if prompt_content is None:
            raise ValueError("PROMPT content is not set or not found! " + \
                f"prompt_id={prompt_id}, prompt_file={prompt_file}")
        prompt_content = self._render_content(prompt_content)
        logger.info("PROMPT: role=%s, content=%s",
            role, WorkflowInterpreter.limit_str(prompt_content))

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
        logger.info("PROMPT: result: %s", WorkflowInterpreter.limit_str(self.workflow.result))


    def execute(self, command: str = None):
        """Execute the commands in the current result"""
        logger.info("EXECUTE: %s", WorkflowInterpreter.limit_str(self.workflow.result))

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


    def check(self, expression: str) -> bool:
        """Check if the status or result is as expected"""
        # parse the expression
        parts = str.split(expression, " ")
        if len(parts) < 3:
            raise ValueError(f"CHECK expression '{expression}' is not valid! " +\
                "Syntax: <variable> <operation> <expected>")

        left = self.get_value(parts[0])

        if parts[1].upper() == "==":
            operation = WorkflowInterpreter.CheckOperation.EQUALS
        elif parts[1].upper() == WorkflowInterpreter.CheckOperation.EQUALS.name:
            operation = WorkflowInterpreter.CheckOperation.EQUALS
        elif parts[1].upper() == WorkflowInterpreter.CheckOperation.CONTAINS.name:
            operation = WorkflowInterpreter.CheckOperation.CONTAINS
        elif parts[1].upper() == WorkflowInterpreter.CheckOperation.MATCHES.name:
            operation = WorkflowInterpreter.CheckOperation.MATCHES
        else:
            operation = None

        right = " ".join(parts[2:])
        right = self.get_value(right, right)

        if left is None or operation is None or right is None:
            raise ValueError(f"CHECK expression '{expression}' is not valid! " +\
                "Syntax: <variable> <operation> <expected>")

        logger.info("CHECK: '%s' %s '%s'",
            right, operation, WorkflowInterpreter.limit_str(left))
        if operation == WorkflowInterpreter.CheckOperation.EQUALS:
            firstline = left.split("\n")[0].strip()
            return right.strip() == firstline
        elif operation == WorkflowInterpreter.CheckOperation.CONTAINS:
            return right.strip() in left
        elif operation == WorkflowInterpreter.CheckOperation.MATCHES:
            return re.search(right, left) is not None


    def success(self):
        """Finish workflow with status SUCCESS"""
        if self.workflow.result is None:
            logger.info("SUCCESS without result")
        else:
            logger.info("SUCCESS result: %s", WorkflowInterpreter.limit_str(self.workflow.result))
        self.workflow.status = Workflow.Status.SUCCESS


    def failed(self, result : str = ''):
        """Finish workflow with status FAILED"""
        if self.workflow.result is None or len(self.workflow.result) == 0:
            if len(result) > 0:
                self.workflow.result = result
                logger.warning("FAILED result: %s", WorkflowInterpreter.limit_str(result))
            else:
                logger.warning("FAILED without result")
        else:
            if len(result) > 0:
                self.workflow.result = result + "\n" + self.workflow.result
            logger.warning("FAILED result: %s", WorkflowInterpreter.limit_str(self.workflow.result))
        self.workflow.status = Workflow.Status.FAILED


    def _render_content(self, content: str)->str:
        """Render variables (the placeholders) values into the content (the template)"""
        # find all matches of {{...}} in the content string
        matches = re.findall(r"{{\w*}}", content)
        for match in matches:
            value = self.get_value(match[2:-2])
            if value is not None:
                content = content.replace(match, value)
        return content


    def get_value(self, name: str, default_value: str = None)->str:
        """Get the value of the variable with the given name"""
        if name is None or len(name) == 0:
            return default_value

        # Check for constants:
        if name.startswith("'") and name.endswith("'"):
            return name[1:-1]
        if len(name) > 100:
            return default_value # that is obviously a constant, not a variable

        # Find in internal (hard-coded) variables:
        if name == self.InternalVariable.STATUS.name:
            return self.workflow.status.name
        if name == self.InternalVariable.RESULT.name or name == "CONTENT":
            if self.workflow.result is None:
                return ""   # variable found, but result is empty
            return self.workflow.result

        # Find in workflow variables:
        if name in self.workflow.variables:
            return self.workflow.variables[name]

        # Find in prompts:
        if name in self.workflow.prompts:
            return self.workflow.prompts[name].content

        # Find in environment variables:
        if name in os.environ:
            return os.environ[name]
        # Not found:
        if default_value is None:
            # it should have been a variable, so log a warning
            logger.warning("Variable %s not found!", name)
        return default_value


    def set_value(self, name: str, value: str)->None:
        """Set the value of the variable with the given name"""
        if name is None or len(name) == 0:
            logger.warning("Variable name for value='%s' is not set!", value)
            return

        # Check for constants:
        if name.startswith("'") and name.endswith("'"):
            logger.warning("Constant %s cannot be set to %s!", name, value)
            return
        if len(name) > 100:
            logger.warning("Variable name '%s' is too long!", name)
            return

        # Try set in internal (hard-coded) variables:
        if name == self.InternalVariable.STATUS.name:
            if value in Workflow.Status.__members__:
                self.workflow.status = Workflow.Status[value]
            else:
                logger.warning("Value '%s' is not a valid STATUS!", value)
            return
        if name == self.InternalVariable.RESULT.name or name == "CONTENT":
            self.workflow.result = value
            return

        # Set in workflow variables:
        self.workflow.variables[name] = value


    @staticmethod
    def limit_str(content: str, length :int= 100)->str:
        """Limit the string length to the specified number of characters"""
        if len(content) > length:
            return content[:length].replace("\n", "\\n") + "..."
        return content.replace("\n", "\\n")


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
