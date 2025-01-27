#!/bin/python
"""
WorkflowInterpreter module  - Interpreter for Workflow instances
"""

import logging
import os
import re
from enum import Enum
import datetime
from dotenv import load_dotenv
from app.util.string_utils import trunc_right, escape_linefeed
from app.agents.agent import AIAgent
from app.agents.agent_factory import AIAgentFactory
from app.agents.prompt import Prompt
from app.agents.prompt_factory import PromptFactory
from app.workflow.activity import Activity
from app.workflow.workflow import Workflow
from app.workflow.workflow_reader import WorkflowReader
from app.workflow.operation import OperationInterpreter
from app.workflow.workflow_writer import WorkflowWriter
from app.workflow.history import History
from app.commands.command import Command
from app.commands.parser import Parser
from app.commands.executor import CommandExecutor
from app.commands.shell_executor import ShellCommandExecutor


load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
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


    def __init__(self, workflow : Workflow = None, parent_interpreter = None):
        self.workflow : Workflow = workflow
        self.agent : AIAgent = None   # will be set from outside
        self.command_executor : CommandExecutor = None  # will be set from outside
        self.max_hits = 3
        self.current_activity = None
        self.id = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.parent_interpreter : WorkflowInterpreter = parent_interpreter

        self.history : History = History()
        self.history_dir : str = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
        if self.parent_interpreter is not None:
            parent = self.parent_interpreter
            while parent.parent_interpreter is not None:
                parent = parent.parent_interpreter
            self.history_dir = os.path.join(self.history_dir, parent.id)
        else:
            self.history_dir = os.path.join(self.history_dir, self.id)


    def run(self, workflow : Workflow)->Workflow.Status:
        """Run the workflow"""
        logger.info("RUN: %s", workflow.name)
        self.workflow = workflow

        self.current_activity = workflow.start
        if self.current_activity is None:
            self.current_activity = workflow.activities[Activity.Kind.START.name]

        while self.current_activity is not None:
            # pre-conditions
            if self.current_activity.hits > self.max_hits:
                self.failed( f"Activity {self.current_activity.name} " +\
                    "has been executed too many times")
                break
            self.current_activity.hits += 1

            # run the activity
            activity_succeeded = True
            try:
                if self.current_activity.kind == Activity.Kind.START:
                    self.start()
                elif self.current_activity.kind == Activity.Kind.SET:
                    activity_succeeded = self.set(self.current_activity.expression)
                elif self.current_activity.kind == Activity.Kind.ASSIGN:
                    activity_succeeded = self.assign(self.current_activity.expression)
                elif self.current_activity.kind == Activity.Kind.CHECK:
                    activity_succeeded = self.check(self.current_activity.expression)
                elif self.current_activity.kind == Activity.Kind.PROMPT:
                    activity_succeeded = self.prompt(prompt_id = self.current_activity.expression)
                elif self.current_activity.kind == Activity.Kind.EXECUTE:
                    activity_succeeded = self.execute(self.current_activity.expression)
                elif self.current_activity.kind == Activity.Kind.CALL:
                    activity_succeeded = self.call(self.current_activity.expression)
                elif self.current_activity.kind == Activity.Kind.SUCCESS:
                    self.success()
                    break
                elif self.current_activity.kind == Activity.Kind.FAILED:
                    self.failed()
                    break
            except Exception as e:
                self.failed(str(e))
                break

            # post-conditions
            if activity_succeeded:
                self.current_activity = self.current_activity.next
                if self.current_activity is None:
                    self.success()
                    break
            else:
                self.current_activity = self.current_activity.other
                if self.current_activity is None:
                    self.failed()
                    break

        # finalisation
        logger.info("DONE:%s with result %s", workflow.name, workflow.status)
        return workflow.status


    def start(self)->None:
        """Start the workflow"""
        logger.info("START: %s", self.workflow.name)
        self.workflow.status = Workflow.Status.DOING
        self._save_history(Activity.Kind.START.value,
            self.workflow.status, self.workflow.result)


    def assign(self, value: str = None)->bool:
        """Assign a prompt to the result (like a "copy" operation)"""
        content = None
        if value is not None:
            content = self.get_value(value)
            content = self._render_content(content)
        if content is None:
            logger.warning("ASSIGN: Value is not set! ")
            self.workflow.status = Workflow.Status.FAILED
            self.workflow.result = "FAILED  \nASSIGN Value is not set!"
            self._save_history(f"{Activity.Kind.ASSIGN.value}: {value}",
                self.workflow.status, self.workflow.result)
            return False
        logger.info("ASSIGN: %s", escape_linefeed(trunc_right(content)))
        self.workflow.result = content

        self._save_history(f"{Activity.Kind.ASSIGN.value}: {value}",
            self.workflow.status, self.workflow.result)
        return True


    def set(self, expression: str = None)->bool:
        """Set a variable value"""
        # parse the expression
        parts = str.split(expression, "=")
        if len(parts) < 2:
            logger.warning("SET expression=%s is not valid! " +\
                "Syntax: <variable>=<value>", expression)
            self.workflow.status = Workflow.Status.FAILED
            self.workflow.result = f"FAILED  \nSET expression={expression} is not valid!"+\
                "Syntax: <variable>=<value>"
            self._save_history(f"{Activity.Kind.SET.value}: {expression}",
                self.workflow.status, self.workflow.result)
            return False

        name = parts[0]
        value = " ".join(parts[1:])
        value = self.get_value(value, value)
        value = self._render_content(value)
        self.set_value(name, value)
        logger.info("SET: %s='%s'", name, escape_linefeed(trunc_right(value)))
        self._save_history(f"{Activity.Kind.SET.value}: {expression}",
            self.workflow.status, self.workflow.result)
        return True


    def prompt(self,
            role : str = Prompt.USER,
            prompt_id: str = None,
            prompt_file: str = None)->bool:
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
            logger.warning("PROMPT content is not set or not found! " + \
                "prompt_id=%s, prompt_file=%s", prompt_id, prompt_file)
            self.workflow.status = Workflow.Status.FAILED
            self.workflow.result = "PROMPT content is not set or not found! " + \
                f"prompt_id={prompt_id}"
            self._save_history(f"{Activity.Kind.PROMPT.value}: {prompt_id}",
                self.workflow.status, self.workflow.result)
            return False

        prompt_content = self._render_content(prompt_content)
        logger.info("PROMPT: role=%s, content=%s", role,
            escape_linefeed(trunc_right(prompt_content)))

        if self.agent is None:
            self.agent = AIAgentFactory.create_agent()

        if Prompt.SYSTEM == role.lower():
            # The system prompt starts a new agent
            self.agent = AIAgentFactory.create_agent()
            self.agent.system(prompt_content)
            self.workflow.result = ""
        elif Prompt.ASSISTANT == role.lower():
            self.agent.advice(None, prompt_content)
            self.workflow.result = prompt_content
        else:   #if Prompt.USER == role.lower():
            self.workflow.result = self.agent.ask(prompt_content)
        logger.info("PROMPT: result: %s", escape_linefeed(trunc_right(self.workflow.result)))
        self._save_history(f"{Activity.Kind.PROMPT.value}: {prompt_id}",
            self.workflow.status, f"{prompt_content}\n\n---\n\n{self.workflow.result}")
        return True


    def execute(self, command: str = None)->bool:
        """Execute the commands in the current result"""
        logger.info("EXECUTE: %s", escape_linefeed(trunc_right(self.workflow.result)))

        if self.command_executor is None:
            logger.error("CommandExecutor is not set")
            self.workflow.status = Workflow.Status.FAILED
            self.workflow.result("FAILED  \nCommandExecutor is not set!")
            self._save_history(f"{Activity.Kind.EXECUTE.value}: {command}",
                self.workflow.status, self.workflow.result)
            return False

        if command is not None and len(command) > 0:
            command = self._render_content(command)
            commands = [Command(Command.SHELL, [command])]
        else:
            commands = Parser().parse(self.workflow.result)
        self.workflow.result = ""
        history_result = ""
        for cmd in commands:
            self.command_executor.execute(cmd)
            history_result += "Input:\n```shell\n"
            for shell_cmd in cmd.cmds:
                self.workflow.result += f"$ {shell_cmd}\n"
                history_result += f"{shell_cmd}\n"
            if len(cmd.output) > 0:
                self.workflow.result += cmd.output + "\n"
                history_result += f"```\n\nOutput:\n```shell\n{cmd.output}\n```\n\n"
            else:
                self.workflow.result += "\n"
                history_result += "```\n\nNo Output\n\n"
        self._save_history(f"{Activity.Kind.EXECUTE.value}: {command}",
            self.workflow.status, history_result)
        return True


    def call(self, workflow_name: str = None) -> bool:
        """Call another workflow as sub-workflow"""
        logger.info("CALL: %s", workflow_name)
        directory = os.path.dirname(self.workflow.filepath)
        if len(directory) == 0:
            directory = None
        try:
            sub_workflow = WorkflowReader.load_from_mdfile(workflow_name, directory)
        except FileNotFoundError:
            logger.warning("Workflow file %s not found", workflow_name)
            self.workflow.status = Workflow.Status.FAILED
            self.workflow.result = "FAILED  \n" + \
                f"Workflow file {workflow_name} in {directory} not found!"
            self._save_history(f"{Activity.Kind.CALL.value}: {workflow_name}",
                self.workflow.status, self.workflow.result)
            return False

        sub_workflow.parent = self.workflow
        sub_workflow.result = self.workflow.result
        for key,value in self.workflow.variables.items():
            sub_workflow.variables[key] = value
        sub_interpreter = WorkflowInterpreter(sub_workflow, self)
        sub_interpreter.agent = self.agent
        sub_interpreter.command_executor = self.command_executor

        ## run the workflow
        sub_status = sub_interpreter.run(sub_workflow)
        logger.info("CALL: Sub-Workflow %s completed with %s, Result:%s",
            workflow_name, sub_status, escape_linefeed(trunc_right(sub_workflow.result)))
        self.workflow.status = sub_status
        self.workflow.result = sub_workflow.result
        for key,value in sub_workflow.variables.items():
            self.workflow.variables[key] = value
        self._save_history(f"{Activity.Kind.CALL.value}: {workflow_name}",
            sub_status, sub_workflow.result)
        return sub_status == Workflow.Status.SUCCESS


    def check(self, expression: str) -> bool:
        """Check if the status or result is as expected"""
        # parse the expression
        parts = str.split(expression, " ")
        if len(parts) < 3:
            logger.warning("CHECK expression '%s' is not valid! ", expression)
            self.workflow.status = Workflow.Status.FAILED
            self.workflow.result = f"CHECK expression {expression} is not valid!\n" +\
                "Syntax: <variable> <operation> <expected>"
            self._save_history(f"{Activity.Kind.CHECK.value}: {expression}",
                self.workflow.status, self.workflow.result)
            return False

        left = self.get_value(parts[0])
        operation = OperationInterpreter.parse_operation(parts[1])
        right = " ".join(parts[2:])
        right = self.get_value(right, right)
        if left is None or operation is None or right is None:
            logger.warning("CHECK expression '%s' is not valid! ", expression)
            self.workflow.status = Workflow.Status.FAILED
            self.workflow.result = f"CHECK expression {expression} is not valid!\n" +\
                "Syntax: <variable> <operation> <expected>"
            self._save_history(f"{Activity.Kind.CHECK.value}: {expression}",
                self.workflow.status, self.workflow.result)
            return False

        logger.info("CHECK: '%s' %s '%s'", right, operation, escape_linefeed(trunc_right(left)))
        self._save_history(f"{Activity.Kind.CHECK.value}: {expression}",
            self.workflow.status, self.workflow.result)
        return OperationInterpreter.interpret_operation(operation, left, right)


    def success(self):
        """Finish workflow with status SUCCESS"""
        if self.workflow.result is None:
            logger.info("SUCCESS without result")
        else:
            logger.info("SUCCESS result: %s", escape_linefeed(trunc_right(self.workflow.result)))
        self.workflow.status = Workflow.Status.SUCCESS
        self._save_history(f"{Activity.Kind.SUCCESS.value}",
            self.workflow.status, self.workflow.result)


    def failed(self, result : str = ''):
        """Finish workflow with status FAILED"""
        if self.workflow.result is None or len(self.workflow.result) == 0:
            if len(result) > 0:
                self.workflow.result = result
                logger.warning("FAILED result: %s", escape_linefeed(trunc_right(result)))
            else:
                logger.warning("FAILED without result")
        else:
            if len(result) > 0:
                self.workflow.result = result + "  \n" + self.workflow.result
            logger.warning("FAILED result: %s", escape_linefeed(trunc_right(self.workflow.result)))
        self.workflow.status = Workflow.Status.FAILED
        self._save_history(f"{Activity.Kind.FAILED.value}",
            self.workflow.status, self.workflow.result)



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


    def _save_history(self, caption : str, status : Workflow.Status, result : str)->None:
        self.history.add_record(caption, status, result)
        WorkflowWriter(self.workflow).save_history(
            current_activity = self.current_activity,
            history = self.history,
            directory = self.history_dir)



if __name__ == "__main__":
    main_workflow = WorkflowReader.load_from_mdfile("sample-project-eval.wf.md")
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
