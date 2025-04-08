"""
ActivityInterpreter module  - Interpreter for Activity instances
"""

import logging
import os
import re
from dotenv import load_dotenv
from app.util.string_utils import escape_linefeed, trunc_right, trunc_middle
from app.agents.agent_factory import AIAgentFactory
from app.agents.prompt import Prompt
from app.commands.command import Command
from app.commands.parser import Parser
from app.workflow.activity import Activity, ActivityVisitor
from app.workflow.workflow import Workflow
from app.workflow.context import Context
from app.workflow.writer import WorkflowWriter
from app.workflow.history import History, HistoryRecord
from app.workflow.operation import OperationInterpreter




load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)




class ActivityInterpreter(ActivityVisitor):
    """Interprets the activities"""

    def __init__(self, context : Context, history : History = None):
        self.context = context
        self.history = history

        self.activity_succeeded = True
        self.is_in_onfailed = False
        self.workflow_ended = False
        self.next_activity : Activity = None



    def visit_start(self, activity: Activity) -> None:
        """Start the workflow"""
        logger.info("START: %s", self.context.workflow.name)
        self.context.status = Workflow.Status.DOING
        self._save_history(activity, Activity.Kind.START.value,
            self.context.status, self.context.result)


    def visit_set(self, activity: Activity) -> None:
        """Set a variable value"""
        # parse the expression
        parts = str.split(activity.expression, "=")
        if len(parts) < 2:
            logger.warning("SET expression=%s is not valid! " +\
                "Syntax: <variable>=<value>", activity.expression)
            self.context.status = Workflow.Status.FAILED
            self.context.result = f"FAILED  \nSET expression={activity.expression}"+\
                " is not valid!\nSyntax: <variable>=<value>"
            self._save_history(activity, f"{Activity.Kind.SET.value}: {activity.expression}",
                self.context.status, self.context.result)
            self.activity_succeeded = False
            return

        name = parts[0]
        value = " ".join(parts[1:])
        value = self.context.get_value(value, value)
        value = self._render_content(value)
        self.context.set_value(name, value)
        logger.info("SET: %s='%s'", name, escape_linefeed(trunc_right(value)))
        self._save_history(activity, f"{Activity.Kind.SET.value}: {activity.expression}",
            self.context.status, self.context.result)
        self.activity_succeeded = True


    def visit_assign(self, activity: Activity) -> None:
        """Assign a prompt to the result (like a "copy" operation)"""
        content = None
        if activity.expression is not None:
            content = self.context.get_value(activity.expression)
            content = self._render_content(content)
        if content is None:
            logger.warning("ASSIGN: Value is not set! ")
            self.context.status = Workflow.Status.FAILED
            self.context.result = "FAILED  \nASSIGN Value is not set!"
            self._save_history(activity, f"{Activity.Kind.ASSIGN.value}: {activity.expression}",
                self.context.status, self.context.result)
            self.activity_succeeded = False
            return

        logger.info("ASSIGN: %s", escape_linefeed(trunc_right(content)))
        self.context.result = content

        self._save_history(activity, f"{Activity.Kind.ASSIGN.value}: {activity.expression}",
            self.context.status, self.context.result)
        self.activity_succeeded = True


    def visit_check(self, activity: Activity) -> None:
        """Check if the status or result is as expected"""
        # parse the expression
        parts = str.split(activity.expression, " ")
        if len(parts) < 3:
            logger.warning("CHECK expression '%s' is not valid! ", activity.expression)
            self.context.status = Workflow.Status.FAILED
            self.context.result = f"CHECK expression {activity.expression}" +\
                " is not valid!\nSyntax: <variable> <operation> <expected>"
            self._save_history(activity, f"{Activity.Kind.CHECK.value}: {activity.expression}",
                self.context.status, self.context.result)
            self.activity_succeeded = False
            return

        left = self.context.get_value(parts[0])
        operation = OperationInterpreter.parse_operation(parts[1])
        right = " ".join(parts[2:])
        right = self.context.get_value(right, right)
        if left is None or operation is None or right is None:
            logger.warning("CHECK expression '%s' is not valid! ", activity.expression)
            self.context.status = Workflow.Status.FAILED
            self.context.result = f"CHECK expression {activity.expression}" +\
                " is not valid!\nSyntax: <variable> <operation> <expected>"
            self._save_history(activity, f"{Activity.Kind.CHECK.value}: {activity.expression}",
                self.context.status, self.context.result)
            self.activity_succeeded = False
            return

        logger.info("CHECK: '%s' %s '%s'", right, operation, escape_linefeed(trunc_right(left)))
        self._save_history(activity, f"{Activity.Kind.CHECK.value}: {activity.expression}",
            self.context.status, self.context.result)
        self.activity_succeeded = OperationInterpreter.interpret_operation(operation, left, right)


    def visit_prompt(self, activity: Activity) -> None:
        """Send a prompt to the AI-agent"""
        # get the prompt content
        role = Prompt.USER
        prompt_id = activity.expression
        prompt_content = None
        if prompt_id is not None:
            prompt_content = self.context.get_value(prompt_id)
            if prompt_id == "System":
                role = Prompt.SYSTEM
            elif prompt_id.startswith("Assistant "):
                role = Prompt.ASSISTANT

        if prompt_content is None:
            logger.warning("PROMPT content is not set or not found! " + \
                "prompt_id=%s", prompt_id)
            self.context.status = Workflow.Status.FAILED
            self.context.result = "PROMPT content is not set or not found! " + \
                f"prompt_id={prompt_id}"
            self._save_history(activity, f"{Activity.Kind.PROMPT.value}: {prompt_id}",
                self.context.status, self.context.result)
            self.activity_succeeded = False
            return

        prompt_content = self._render_content(prompt_content)
        logger.info("PROMPT: role=%s, content=%s", role,
            escape_linefeed(trunc_right(prompt_content)))

        if self.context.agent is None:
            self.context.agent = AIAgentFactory.create_agent()

        history_record = self._save_history(activity, f"{Activity.Kind.PROMPT.value}: {prompt_id}",
            self.context.status,
            f"{prompt_content}\n\n---\n\n...")
        if Prompt.SYSTEM == role.lower():
            # The system prompt starts a new agent
            self.context.agent = AIAgentFactory.create_agent()
            self.context.agent.system(prompt_content)
            self.context.result = ""
        elif Prompt.ASSISTANT == role.lower():
            self.agent.advice(None, prompt_content)
            self.context.result = prompt_content
        else:   #if Prompt.USER == role.lower():
            self.context.result = self.context.agent.ask(prompt_content)
        logger.info("PROMPT: result: %s",
                    escape_linefeed(trunc_right(self.context.result)))
        self._update_history(history_record, f"{prompt_content}\n\n---\n\n{self.context.result}")
        self.activity_succeeded = True


    def visit_ask(self, activity: Activity) -> None:
        """Ask a question to the user via console"""
        logger.info("EXECUTE: %s", escape_linefeed(trunc_right(self.context.result)))
        history_record = self._save_history(activity, f"{Activity.Kind.ASK.value} ",
            self.context.status, "...")
        history_result = f"Input:\n{self.context.result}\n\n"
        print(self.context.result)
        # catch Strg+C to stop the workflow
        try:
            self.context.result = input()
            self.activity_succeeded = True
        except KeyboardInterrupt:
            self.context.status = Workflow.Status.FAILED
            self.context.result = "FAILED  \nInterrupted by user!"
            self.activity_succeeded = False
        history_result += f"Output:\n{self.context.result}\n\n"
        self._update_history(history_record, history_result)


    def visit_execute(self, activity: Activity) -> None:
        """Execute the commands in the current result"""
        logger.info("EXECUTE: %s", escape_linefeed(trunc_right(self.context.result)))

        command = activity.expression
        if self.context.command_executor is None:
            logger.error("CommandExecutor is not set")
            self.context.status = Workflow.Status.FAILED
            self.context.result("FAILED  \nCommandExecutor is not set!")
            self._save_history(activity, f"{Activity.Kind.EXECUTE.value}: {command}",
                self.context.status, self.context.result)
            self.activity_succeeded = False
            return

        if command is not None and len(command) > 0:
            command = self._render_content(command)
            commands = [Command(Command.SHELL, [command])]
        else:
            commands = Parser().parse(self.context.result)
        history_record = self._save_history(activity, f"{Activity.Kind.EXECUTE.value}: {command}",
            self.context.status, "...")
        self.context.result = ""
        history_result = ""
        for cmd in commands:
            self.context.command_executor.execute(cmd)
            history_result += "Input:\n```shell\n"
            for shell_cmd in cmd.cmds:
                self.context.result += f"$ {shell_cmd}\n"
                history_result += f"{shell_cmd}\n"
            if len(cmd.output) > 0:
                self.context.result += cmd.output + "\n"
                history_result += f"```\n\nOutput:\n```shell\n{cmd.output}\n```\n\n"
            else:
                self.context.result += "\n"
                history_result += "```\n\nNo Output\n\n"
        self._update_history(history_record, history_result)
        self.activity_succeeded = True


    def visit_call(self, activity: Activity) -> None:
        """Visit the call activity"""
        logger.warning("CALL: %s should be handled in WorkflowInterpreter", activity.expression)
        self.activity_succeeded = True


    def visit_success(self, activity: Activity) -> None:
        """Finish workflow with status SUCCESS"""
        # is there an on_success event-handler? if yes, the go along there
        on_success = self.context.workflow.on_success
        if on_success is not None and on_success.hits == 0:
            self.next_activity = on_success
            self.workflow_ended = False
            return

        # finish the workflow
        if self.context.result is None:
            logger.info("SUCCESS without result")
        else:
            logger.info("SUCCESS result: %s",
                        escape_linefeed(trunc_right(self.context.result)))
        self.context.status = Workflow.Status.SUCCESS
        self._save_history(activity, f"{Activity.Kind.SUCCESS.value}",
            self.context.status, self.context.result)
        self.workflow_ended = True

    def success(self) -> None:
        """Manual Finish workflow with status SUCCESS"""
        self.visit_success(None)


    def visit_failed(self, activity: Activity) -> None:
        """Finish workflow with status FAILED"""
        # is there an on_failed event-handler? if yes, the go along there
        on_failed = self.context.workflow.on_failed
        if on_failed is not None and on_failed.hits == 0:
            self.next_activity = on_failed
            self.is_in_onfailed = True
            self.workflow_ended = False
            return

        # finish the workflow
        if self.context.result is None or len(self.context.result) == 0:
            logger.warning("FAILED without result")
        else:
            logger.warning("FAILED result: %s",
                           escape_linefeed(trunc_right(self.context.result)))
        self.context.status = Workflow.Status.FAILED
        self._save_history(activity, f"{Activity.Kind.FAILED.value}",
            self.context.status, self.context.result)
        self.workflow_ended = True

    def failed(self, result : str = '') -> bool:
        """Finish workflow with status FAILED"""
        # is there an on_failed event-handler? if yes, the go along there
        on_failed = self.context.workflow.on_failed
        if on_failed is not None and on_failed.hits == 0:
            if len(result) > 0:
                self.context.result = result
                self.context.status = Workflow.Status.FAILED
            self.next_activity = on_failed
            self.is_in_onfailed = True
            return False

        # finish the workflow
        if self.context.result is None or len(self.context.result) == 0:
            if len(result) > 0:
                self.context.result = result
                logger.warning("FAILED result: %s", escape_linefeed(trunc_right(result)))
            else:
                logger.warning("FAILED without result")
        else:
            if len(result) > 0:
                self.context.result = result + "  \n" + self.context.result
            logger.warning("FAILED result: %s",
                           escape_linefeed(trunc_right(self.context.result)))
        self.context.status = Workflow.Status.FAILED
        self._save_history(None, f"{Activity.Kind.FAILED.value}",
            self.context.status, self.context.result)
        return True


    def visit_on(self, activity: Activity) -> None:
        """Visit the on activity"""
        self._save_history(activity, f"{activity.name}",
            self.context.status, self.context.result)
        self.activity_succeeded = True



    def _render_content(self, content: str)->str:
        """Render variables (the placeholders) values into the content (the template)"""
        # find all matches of {{...}} in the content string
        matches = re.findall(r"{{\w*}}", content)
        for match in matches:
            value = self.context.get_value(match[2:-2])
            if value is not None:
                content = content.replace(match, value)
        return content


    def _save_history(self, activity : Activity, caption : str,
                      status : Workflow.Status, result : str)->HistoryRecord:
        if self.history is None:
            logger.info("History-Record: caption=%s, status=%s, result=%s", caption, status, result)
            return None
        record = self.history.add_record(caption,status,
                                         trunc_middle(result,self.history.max_record_length))
        WorkflowWriter(self.context.workflow).save_history(
            current_activity = activity,
            context = self.context,
            history = self.history,
            directory = self.history.history_dir)
        return record


    def _update_history(self, record: HistoryRecord, result: str)->None:
        if self.history is None:
            return
        record.result = trunc_middle(result,self.history.max_record_length)
        WorkflowWriter(self.context.workflow).save_history(
            current_activity = None,
            context = self.context,
            history = self.history,
            directory = self.history.history_dir)
