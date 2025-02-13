#!/bin/python
"""
WorkflowInterpreter module  - Interpreter for Workflow instances
"""

import logging
import os
import sys
import datetime
from dotenv import load_dotenv
from app.util.string_utils import trunc_right, escape_linefeed, trunc_middle
from app.agents.agent_factory import AIAgentFactory
from app.workflow.activity import Activity
from app.workflow.workflow import Workflow
from app.workflow.workflow_reader import WorkflowReader
from app.workflow.workflow_writer import WorkflowWriter
from app.workflow.context import Context
from app.workflow.history import History, HistoryRecord
from app.workflow.activity_interpreter import ActivityInterpreter
from app.commands.shell_executor import ShellCommandExecutor


load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)




class WorkflowInterpreter:
    """The base class for all WorkflowInterpreter implementations"""


    def __init__(self, workflow : Workflow, parent_interpreter = None):
        self.id = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.workflow = workflow
        self.context : Context = None

        self.parent_interpreter : WorkflowInterpreter = parent_interpreter
        self.max_activity_hits = 3

        history_max_length = int(os.getenv('AI_MAX_PROMPT_LENGTH', '2000'))
        history_dir : str = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
        if self.parent_interpreter is not None:
            parent = self.parent_interpreter
            while parent.parent_interpreter is not None:
                parent = parent.parent_interpreter
            history_dir = os.path.join(history_dir, parent.id)
        else:
            history_dir = os.path.join(history_dir, self.id)
        self.history : History = History( history_dir, history_max_length )


    # return a tuple containing Workflow.Status and str
    def run(self, context : Context) -> tuple[Workflow.Status, str]:
        """Run the workflow"""
        self.context = context
        logger.info("RUN: %s", self.workflow.name)
        activity_interpreter = ActivityInterpreter(self.context, self.history)

        current_activity = self.workflow.start
        if current_activity is None:
            current_activity = self.workflow.activities[Activity.Kind.START.name]

        while current_activity is not None:
            # pre-conditions
            if current_activity.hits > self.max_activity_hits:
                msg = f"Activity {current_activity.name} has been executed too many times"
                if activity_interpreter.failed(msg):
                    break
            current_activity.hits += 1

            # run the activity
            try:
                if current_activity.kind == Activity.Kind.CALL:
                    # handle call (with workflow-interpreters) outside of activity interpreter
                    activity_interpreter.activity_succeeded = \
                        self._call(current_activity)
                else:
                    current_activity.accept(activity_interpreter)

            except Exception as e:
                if activity_interpreter.failed(str(e)):
                    break

            # post-conditions
            if activity_interpreter.workflow_ended:
                break
            if activity_interpreter.next_activity is not None:
                current_activity = activity_interpreter.next_activity
                activity_interpreter.next_activity = None
                continue
            if activity_interpreter.activity_succeeded:
                current_activity = current_activity.next
                if current_activity is None:
                    if activity_interpreter.is_in_onfailed:
                        activity_interpreter.failed()
                        break
                    activity_interpreter.success()
                    if activity_interpreter.workflow_ended:
                        break
            else:
                current_activity = current_activity.other
                if current_activity is None:
                    if activity_interpreter.failed():
                        break

        # finalization
        logger.info("DONE:%s with result %s", self.workflow.name, self.context.status)
        return (self.context.status, self.context.result)



    def _call(self, activity : Activity) -> bool:
        """Call another workflow as sub-workflow"""
        sub_workflow_name = activity.expression
        logger.info("CALL: %s", sub_workflow_name)
        directory = os.path.dirname(self.workflow.filepath)
        if len(directory) == 0:
            directory = None
        try:
            sub_workflow = WorkflowReader().load_from_mdfile(sub_workflow_name, directory)
        except FileNotFoundError:
            logger.warning("Workflow file %s not found", sub_workflow_name)
            self.context.status = Workflow.Status.FAILED
            self.context.result = "FAILED  \n" + \
                f"Workflow file {sub_workflow_name} in {directory} not found!"
            self._save_history(activity, f"{Activity.Kind.CALL.value}: {sub_workflow_name}",
                               self.context.status, self.context.result)
            return False

        sub_workflow.parent = self.workflow

        ## run the workflow
        sub_interpreter = WorkflowInterpreter(sub_workflow, parent_interpreter=self )
        sub_context = Context(sub_workflow, self.context.agent, self.context.command_executor)
        for key,value in self.context.variables.items():
            sub_context.variables[key] = value
        sub_context.result = self.context.result
        history_record = self._save_history(activity,
                f"{Activity.Kind.CALL.value}: {sub_workflow_name}", Workflow.Status.DOING, "...")
        (sub_status, sub_result) = sub_interpreter.run(sub_context)
        logger.info("CALL: Sub-Workflow %s completed with %s, Result:%s",
            sub_workflow_name, sub_status, escape_linefeed(trunc_right(sub_result)))
        self.context.status = sub_status
        self.context.result = sub_result
        for key,value in sub_context.variables.items():
            self.context.variables[key] = value
        self._update_history(history_record, sub_status, sub_result)
        return sub_status == Workflow.Status.SUCCESS


    def _save_history(self, current_activity : Activity, caption : str,
                      status : Workflow.Status, result : str)->HistoryRecord:
        if status is None:
            status = self.workflow.status
        record = self.history.add_record(caption,status,
                                trunc_middle(result,self.history.max_record_length))
        WorkflowWriter(self.workflow).save_history(
            current_activity = current_activity,
            context = self.context,
            history = self.history,
            directory = self.history.history_dir)
        return record


    def _update_history(self, record: HistoryRecord, status: Workflow.Status, result: str)->None:
        if self.history is None:
            return
        record.status = status
        record.result = trunc_middle(result,self.history.max_record_length)
        WorkflowWriter(self.context.workflow).save_history(
            current_activity = None,
            context = self.context,
            history = self.history,
            directory = self.history.history_dir)


if __name__ == "__main__":
    main_workflow = WorkflowReader().load_from_mdfile("sample-project-eval.wf.md")
    main_interpreter = WorkflowInterpreter(main_workflow)

    ## run the workflow
    main_context = Context(main_workflow, AIAgentFactory.create_agent(), ShellCommandExecutor())
    (main_status, main_result) = main_interpreter.run(main_context)
    if main_status == Workflow.Status.SUCCESS:
        print(f"Workflow completed with SUCCESS, Result:\n{main_result}")
        sys.exit(0)
    else:
        print(f"Workflow completed with FAILED, Result:\n{main_result}")
        sys.exit(1)
