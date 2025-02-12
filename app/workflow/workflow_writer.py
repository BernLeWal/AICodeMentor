#!/bin/python
"""
WorkflowWriter module  - Saving Workflow instances to file
"""

import os
import logging
from enum import Enum
from dotenv import load_dotenv
from app.workflow.activity import Activity
from app.workflow.history import History
from app.workflow.workflow import Workflow
from app.workflow.context import Context
from app.workflow.workflow_reader import WorkflowReader


load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


class WorkflowMdSection(Enum):
    """Sections inside a Markdown file"""
    GENERAL = ""
    VARIABLES = "## Variables"

    WORKFLOW = "# Workflow"
    PROMPTS = "# Prompts"
    HISTORY = "# History"

    def __str__(self):
        return self.name


class WorkflowWriter:
    """Writes Workflow instances to file"""

    WORKFLOWS_DIR = os.getenv('WORKFLOWS_DIR', './workflows')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
    LOGFILES_DIR = os.getenv('LOGFILES_DIR', './log')

    def __init__(self, workflow : Workflow):
        self.workflow : Workflow = workflow
        self.file = None
        self.visited_activities = set()


    def save_definition(self, filepath : str,
        directory = None, overwrite = True):
        """Saves Workflow definition to file"""
        if directory is None:
            directory = os.path.abspath(WorkflowWriter.WORKFLOWS_DIR)
        self._open_file(filepath, directory, overwrite)

        # First section: general
        self.file.write(f"# {self.workflow.name}\n\n")
        self.file.write(f"{self.workflow.description}\n\n")

        # Second section: workflow flow-chart
        self.file.write(f"{WorkflowMdSection.WORKFLOW.value}\n\n")
        self.file.write("```mermaid\n")
        self.file.write("flowchart TD\n")
        self._write_activity(self.workflow.start)
        self.file.write("```\n\n")

        # Third section: Prompts
        self.file.write(f"{WorkflowMdSection.PROMPTS.value}\n\n")
        for name, prompt in self.workflow.prompts:
            self.file.write(f"## {name}\n\n{prompt}\n\n")

        self.file.close()


    def save_history(self, current_activity : Activity, context : Context, history : History,
        filepath : str = None, directory = None, overwrite = True):
        """Saves Workflow instance to file"""
        if directory is None:
            directory = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if filepath is None:
            filepath = os.path.basename(self.workflow.filepath)
            filepath = f"{self.workflow.instance_nr:02d}_" + filepath.replace(".wf.md", ".wfh.md")
        else:
            filepath = os.path.basename(filepath)
        self._open_file(filepath, directory, overwrite)

        # First section: general
        self.file.write(f"# {self.workflow.name}\n\n")
        self.file.write(f"- filepath={self.workflow.filepath}\n")
        self.file.write("\n")

        # Second section: workflow flow-chart
        self.file.write(f"{WorkflowMdSection.WORKFLOW.value}\n")
        self.file.write("```mermaid\n")
        self.file.write("flowchart TD\n")
        self._write_activity(self.workflow.start)
        if self.workflow.on_success is not None:
            self.file.write(f"\n  %% Event-handler: {self.workflow.on_success.name}\n")
            self._write_activity(self.workflow.on_success)
        if self.workflow.on_failed is not None:
            self.file.write(f"\n  %% Event-handler: {self.workflow.on_failed.name}\n")
            self._write_activity(self.workflow.on_failed)
        if current_activity is not None:
            self.file.write(f"\n  style {current_activity.name} " + \
                "stroke:#000,stroke-width:4px,fill:#80a0ff\n")
        self.file.write("```\n\n")

        if context is not None:
            self.file.write(f"{WorkflowMdSection.VARIABLES.value}:  \n")
            for key, value in context.variables.items():
                if len(value) > 0 and value.find('\n')>0:
                    self.file.write(f"- **{key}**:  \n{value}  \n")
                else:
                    self.file.write(f"- **{key}**={value}  \n")
            self.file.write("\n\n")

        # Third section: History
        self.file.write(f"{WorkflowMdSection.HISTORY.value}\n\n")
        counter = 1
        for record in history.records:
            self.file.write(f"## {counter}. {record.activity_caption} " +\
                f" => {record.status}\n")
            self.file.write(f"<!-- ts={record.timestamp} -->\n")
            if record.result is not None and len(record.result) > 0:
                self.file.write(f"{record.result}\n\n")
            else:
                self.file.write("\n")
            counter += 1

        self.file.flush()
        self.file.close()


    def _open_file(self, filepath : str, directory, overwrite = True):
        directory = os.path.abspath(directory)
        abs_file_path = os.path.join(directory, filepath)
        if overwrite is True or not os.path.exists(abs_file_path):
            self.file = open(abs_file_path, 'w', encoding='utf-8')
        else:
            raise FileExistsError(f"File {abs_file_path} already exists")


    def _write_activity(self, activity : Activity, recursive : bool = True) -> None:
        if activity is None:
            return
        if activity in self.visited_activities:
            return
        # declare the activity
        self.file.write(f"  {activity.name}")
        if activity.kind == Activity.Kind.START:
            self.file.write("@{ shape: f-circ, label:\"start\"}")
        elif activity.kind == Activity.Kind.SUCCESS:
            self.file.write("@{ shape: stadium  }")
        elif activity.kind == Activity.Kind.FAILED:
            self.file.write("@{ shape: stadium  }")
        elif activity.kind == Activity.Kind.ON:
            self.file.write("@{ shape: stadium  }")
        elif activity.kind == Activity.Kind.CHECK:
            self.file.write("{" + f"{activity.expression}" + "}")
        elif activity.kind == Activity.Kind.CALL:
            self.file.write(f"[[{activity.expression}]]")
        elif activity.kind == Activity.Kind.EXECUTE:
            self.file.write(f"[\"{activity.kind.value}: {activity.expression}\"]")
        else:
            self.file.write(f"[{activity.kind.value}: {activity.expression}]")
        self.file.write("\n")
        self.visited_activities.add(activity)

        # define the flow to the next activity
        if activity.next is not None:
            self.file.write(f"  {activity.name} --> ")
            if activity.kind == Activity.Kind.CHECK:
                self.file.write("|TRUE| ")
            self.file.write(f"{activity.next.name}\n")
            if recursive is True:
                self._write_activity(activity.next)
        if activity.other is not None:
            self.file.write(f"  {activity.name} --> ")
            if activity.kind == Activity.Kind.CHECK:
                self.file.write("|FALSE| ")
            elif activity.kind == Activity.Kind.CALL:
                self.file.write("|FAILED| ")
            self.file.write(f"{activity.other.name}\n")
            if recursive is True:
                self._write_activity(activity.other)


if __name__ == '__main__':
    MAIN_FILENAME = "sample-project-eval.wf.md"
    main_workflow = WorkflowReader.load_from_mdfile(MAIN_FILENAME)

    main_writer = WorkflowWriter(main_workflow)
    history_dir = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
    main_writer.save_history(
        current_activity = main_workflow.start,
        context = None,
        history = History(history_dir) )
