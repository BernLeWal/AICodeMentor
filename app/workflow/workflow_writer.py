#!/bin/python
"""
WorkflowWriter module  - Saving Workflow instances to file
"""

import os
import logging
from enum import Enum
from dotenv import load_dotenv
from app.workflow.activity import Activity
from app.workflow.activity_writer import ActivityWriter
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


    def save_definition(self, filepath : str, directory = None, overwrite = True):
        """Saves Workflow definition to file"""
        if directory is None:
            directory = os.path.abspath(WorkflowWriter.WORKFLOWS_DIR)

        file = self._open_file(filepath, directory, overwrite)
        self._write_general(file)
        self._write_flowchart(file)
        self._write_prompts(file)
        file.close()


    def save_history(self, current_activity : Activity, context : Context, history : History,
        filepath : str = None, directory = None, overwrite = True):
        """Saves Workflow execution with history to a file"""
        if directory is None:
            directory = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if filepath is None:
            filepath = os.path.basename(self.workflow.filepath)
            filepath = f"{self.workflow.instance_nr:02d}_" + filepath.replace(".wf.md", ".wfh.md")
        else:
            filepath = os.path.basename(filepath)

        file = self._open_file(filepath, directory, overwrite)
        self._write_general(file, include_description = False, write_workflow_path = True)
        self._write_flowchart(file, current_activity)
        self._write_variables(file, context)
        self._write_history(file, history)
        file.flush()
        file.close()


    def _open_file(self, filepath : str, directory, overwrite = True):
        directory = os.path.abspath(directory)
        abs_file_path = os.path.join(directory, filepath)
        if overwrite is True or not os.path.exists(abs_file_path):
            return open(abs_file_path, 'w', encoding='utf-8')
        else:
            raise FileExistsError(f"File {abs_file_path} already exists")


    def _write_general(self, file,
                       include_description : bool = True, write_workflow_path : bool = False):
        """First section: general"""
        file.write(f"# {self.workflow.name}\n\n")
        if include_description:
            file.write(f"{self.workflow.description}\n")
        if write_workflow_path:
            file.write(f"- filepath={self.workflow.filepath}\n")
        file.write("\n")


    def _write_flowchart(self, file, current_activity = None):
        """"Second section: flowchart of the workflow"""

        file.write(f"{WorkflowMdSection.WORKFLOW.value}\n")
        file.write("```mermaid\n")
        file.write("flowchart TD\n")

        activity_writer = ActivityWriter(file)
        if self.workflow.start is not None:
            self.workflow.start.accept(activity_writer)

        if self.workflow.on_success is not None:
            file.write(f"\n  %% Event-handler: {self.workflow.on_success.name}\n")
            self.workflow.on_success.accept(activity_writer)

        if self.workflow.on_failed is not None:
            file.write(f"\n  %% Event-handler: {self.workflow.on_failed.name}\n")
            self.workflow.on_failed.accept(activity_writer)

        # highlight the current activity
        if current_activity is not None:
            file.write(f"\n  style {current_activity.name} " + \
                "stroke:#000,stroke-width:4px,fill:#80a0ff\n")
        file.write("```\n\n")



    def _write_prompts(self, file):
        """Third section: Prompts"""
        file.write(f"{WorkflowMdSection.PROMPTS.value}\n\n")
        for name, prompt in self.workflow.prompts.items():
            file.write(f"## {name}\n\n{prompt.content}\n\n")


    def _write_variables(self, file, context : Context):
        if context is not None:
            file.write(f"{WorkflowMdSection.VARIABLES.value}:  \n")
            for key, value in context.variables.items():
                if len(value) > 0 and value.find('\n')>0:
                    file.write(f"- **{key}**:  \n{value}  \n")
                else:
                    file.write(f"- **{key}**={value}  \n")
            file.write("\n\n")


    def _write_history(self, file, history : History):
        """Third section: History"""
        file.write(f"{WorkflowMdSection.HISTORY.value}\n\n")
        counter = 1
        for record in history.records:
            file.write(f"## {counter}. {record.activity_caption} " +\
                f" => {record.status}\n")
            file.write(f"<!-- ts={record.timestamp} -->\n")
            if record.result is not None and len(record.result) > 0:
                file.write(f"{record.result}\n\n")
            else:
                file.write("\n")
            counter += 1



if __name__ == '__main__':
    MAIN_FILENAME = "sample-project-eval.wf.md"
    main_workflow = WorkflowReader().load_from_mdfile(MAIN_FILENAME)

    main_writer = WorkflowWriter(main_workflow)
    history_dir = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
    main_writer.save_definition(
        filepath = os.path.basename(MAIN_FILENAME),
        directory = history_dir
    )
    main_writer.save_history(
        current_activity = main_workflow.start,
        context = None,
        history = History(history_dir) )
