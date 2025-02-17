#!/bin/python
"""
WorkflowReader module  - Reading/Loading Workflow from file and generate Workflow instance
"""

import os
import re
import logging
from enum import Enum
from dotenv import load_dotenv
from app.agents.prompt import Prompt
from app.workflow.activity import Activity
from app.workflow.workflow import Workflow


load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


class WorkflowMdSection(Enum):
    """Sections inside a Markdown file"""
    NONE = ""
    WORKFLOW = "# Workflow"
    PROMPTS = "# Prompts"

    def __str__(self):
        return self.name


class WorkflowReader:
    """
    The base class for all WorkflowReader implementations
    see [docs/workflow.md](../../docs/workflow.md) for file-format description.
    """

    WORKFLOWS_DIR = os.getenv('WORKFLOWS_DIR', './workflows')

    def __init__(self):
        self.workflow = None


    def load_from_mdfile(self, filename: str, directory = None) -> Workflow:
        """
        Load Workflow definition from a markdown file
        :param filename: The name of the file
        """
        self.workflow = Workflow(filename)

        if directory is None:
            directory = os.path.abspath(WorkflowReader.WORKFLOWS_DIR)
        else:
            directory = os.path.abspath(directory)
        self.workflow.directory = directory
        abs_file_path = os.path.join(directory, filename)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        self._parse_content(content)
        return self.workflow


    def load_from_string(self, content : str) -> Workflow:
        """Load Workflow definition from a string"""
        self.workflow = Workflow("")
        self._parse_content(content.split('\n'))
        return self.workflow


    def _parse_content(self, content: list):
        section = WorkflowMdSection.NONE

        content_iter = iter(content)
        line = ''
        while line is not None:
            line_strip = line.strip()
            if line_strip.startswith('# '):
                section = WorkflowReader._check_section(line_strip)
                if section == WorkflowMdSection.NONE:
                    self.workflow.name = line.replace('# ', '').strip()
            elif section == WorkflowMdSection.NONE:
                if len(line_strip)>0 and line_strip != '\n':
                    self.workflow.description += line
            elif section == WorkflowMdSection.WORKFLOW:
                line = self._parse_section_workflow(line, content_iter)
                continue
            elif section == WorkflowMdSection.PROMPTS:
                line = self._parse_section_prompts(line, content_iter)
                continue

            # fetch next line
            try:
                line = next(content_iter)
            except StopIteration:
                break

        # after the loop: set the start, on_success, and on_failed activities
        if self.workflow.start is None:
            self.workflow.start = self.workflow.activities[Activity.Kind.START.name]
        if self.workflow.on_failed is None:
            on_failed_name = f"{Activity.Kind.ON.name}_{Activity.Kind.FAILED.name}"
            if on_failed_name in self.workflow.activities:
                self.workflow.on_failed = self.workflow.activities[on_failed_name]
        if self.workflow.on_success is None:
            on_success_name = f"{Activity.Kind.ON.name}_{Activity.Kind.START.name}"
            if on_success_name in self.workflow.activities:
                self.workflow.on_success = self.workflow.activities[on_success_name]


    @staticmethod
    def _check_section(line_strip : str) -> WorkflowMdSection:
        if line_strip.startswith('# Workflow'):
            return WorkflowMdSection.WORKFLOW
        if line_strip.startswith('# Prompts'):
            return WorkflowMdSection.PROMPTS
        return WorkflowMdSection.NONE


    def _parse_section_workflow(self, line: str, content_iter) -> str:
        in_mermaid = False
        in_flowchart = False

        while True:
            line_strip = line.strip()
            if line_strip.startswith('# '): # next section --> end of workflow section
                return line_strip

            if line_strip.startswith('```mermaid'):
                in_mermaid = True
            elif in_mermaid and line_strip.startswith('flowchart'):
                in_flowchart = True
            elif line_strip.startswith('```'):
                in_mermaid = False
                in_flowchart = False
            elif len(line_strip) > 0 and in_mermaid and in_flowchart:
                self._parse_flowchart_line(line_strip)

            # fetch next
            try:
                line = next(content_iter)
            except StopIteration:
                return None


    def _parse_section_prompts(self, line: str, content_iter) -> str:
        current_content = ''
        current_role = None
        current_key = ''

        while True:
            line_strip = line.strip()
            if line_strip.startswith('# '): # next section --> end of workflow section
                return line_strip

            if line_strip.startswith('## User'):
                if len(current_content) > 0:
                    self.workflow.prompts[current_key] = Prompt(current_role, current_content)
                    current_content = ''
                current_role = Prompt.USER
                current_key = line_strip.replace('## ', '').strip()
            elif line_strip.startswith('## Assistant'):
                if len(current_content) > 0:
                    self.workflow.prompts[current_key] = Prompt(current_role, current_content)
                    current_content = ''
                current_role = Prompt.ASSISTANT
                current_key = line_strip.replace('## ', '').strip()
            elif line_strip.startswith('## System'):
                if len(current_content) > 0:
                    self.workflow.prompts[current_key] = Prompt(current_role, current_content)
                    current_content = ''
                current_role = Prompt.SYSTEM
                current_key = line_strip.replace('## ', '').strip()
            else:
                if current_role is not None:
                    current_content += line

            # fetch next
            try:
                line = next(content_iter)
            except StopIteration:
                break

        if len(current_content) > 0:
            if current_key is not None:
                self.workflow.prompts[current_key] = Prompt(current_role, current_content)
        return None


    def _parse_flowchart_line(self, line : str) -> None:
        # Remove comments
        if line.startswith("%%"):
            return

        # Check if line contains a flow definition (activity -> activity)
        pos = line.find('-->')
        if pos > 0:
            left = line[:pos].strip()
            self._parse_activity(left)
            right = line[pos+3:].strip()
            self._parse_activity(right)

            self._parse_flow(line, left, right)
        else:
            # Parse the activity
            self._parse_activity(line)


    def _parse_flow(self, line: str, left: str, right: str) -> None:
        attr = ''

        match = re.search(r"([A-Z_]*)[@\{\[]", left)
        if match is not None:
            left = match.group(1)

        match = re.search(r"(\|.*\|)?\s*\s*([A-Z_]*)[@\{\[]?", right)
        if match is not None:
            attr = match.group(1)
            if attr is None:
                attr = ''
            if len(attr) > 2:
                attr = attr[1:-1].strip()
            right = match.group(2)

        left_activity = self.workflow.activities[left]
        right_activity = self.workflow.activities[right]
        if attr is None or len(attr) == 0:
            left_activity.next = right_activity
        elif attr.upper() in Activity.Failed.__members__:
            left_activity.other = right_activity
        elif attr.upper() in Activity.Succeeded.__members__:
            left_activity.next = right_activity
        else:
            raise ValueError(f"Invalid flow attribute '{attr}' in flowchart line '{line}'! " + \
                "For positive check results use: YES, TRUE, '', or no attribute. " +\
                "For negative check results use: NO, FALSE, OTHER, ELSE, or FAILED.")

        logger.debug("Flow-Parsed: %s --> %s with attr=%s", left, right, attr)


    def _parse_activity(self, line : str) -> None:
        activity_name = ''
        activity_expr = ''
        match = re.search(r"(\|.*\|)?\s*([A-Z_]*)[@\{\[]?(.*)?[\}\]]?", line)
        if match is not None:
            activity_name = match.group(2)
            activity_expr = match.group(3)
            if activity_expr.endswith(']') or activity_expr.endswith('}'):
                activity_expr = activity_expr[:-1]
            # when activity_expr is in additional brackets, remove them
            if activity_expr.startswith('(') and activity_expr.endswith(')'):
                activity_expr = activity_expr[1:-1]
            if activity_expr.startswith('[') and activity_expr.endswith(']'):
                activity_expr = activity_expr[1:-1]
            if activity_expr.startswith('"') and activity_expr.endswith('"'):
                activity_expr = activity_expr[1:-1]
        else:
            activity_name = line
        if activity_expr.startswith('{') and not activity_name.startswith('PARAMS'):
            activity_expr = ''  # ignore mermaid visualisation defs
        if activity_expr.find(':') > 0:
            # ignore mermaid visualisation prefix
            activity_expr = activity_expr[activity_expr.find(':')+1:].strip()
        logger.debug("Activity-Parsed: '%s' => name=%s, expr=%s",
            line, activity_name, activity_expr)

        if activity_name not in self.workflow.activities:
            # Create a new activity
            pos = activity_name.find('_')
            if pos > 0:
                activity_kindname = activity_name[:pos]
            else:
                activity_kindname = activity_name

            if activity_kindname == "PARAMS":
                # Process workflow parameters
                self._parse_params(activity_expr)
            else:
                # Process activity kind and create activity
                activity_kind = Activity.parse_kind(activity_kindname)
                if activity_kind is None:
                    raise ValueError(f"Invalid Activity prefix! '{activity_kindname}' " + \
                        "not found in Activity.Kind enumeration.")
                activity = Activity(activity_kind, activity_name, activity_expr)
                self.workflow.activities[activity_name] = activity
        else:
            # Update an existing activity
            activity = self.workflow.activities[activity_name]
            if activity_expr is not None and len(activity_expr) > 0:
                activity.expression = activity_expr


    def _parse_params(self, activity_expr : str) -> None:
        match = re.search(r'"(.*)"', activity_expr)
        if not match is None:
            activity_expr = match.group(1)
        params = activity_expr.split(',')
        for param in params:
            param = param.strip()
            if len(param) > 0:
                if param.find('=') > 0:
                    param_key, param_value = param.split('=')
                    self.workflow.params[param_key] = param_value
                else:
                    self.workflow.params[param] = ''



if __name__ == '__main__':
    MAIN_FILENAME = "sample-project-eval.wf.md"
    main_workflow = WorkflowReader().load_from_mdfile(MAIN_FILENAME)
    print(f"Loaded workflow: {main_workflow.name}")
    print(f"Description: {main_workflow.description}\n")

    print("Loaded parameters:")
    for key, value in main_workflow.params.items():
        print(f"  {key}: {value}")

    print("\nLoaded activities:")
    for key, main_activity in main_workflow.activities.items():
        print(f"  {key}: {main_activity}")

    print("\nLoaded prompts:")
    for key, prompt in main_workflow.prompts.items():
        print(f"  {key}: {prompt}")

    print(f"\nStart activity:      {main_workflow.start}")
    print(f"On_Success activity: {main_workflow.on_success}")
    print(f"On_Failed activity:  {main_workflow.on_failed}")
