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
    """The base class for all WorkflowReader implementations"""

    WORKFLOWS_DIR = os.getenv('WORKFLOWS_DIR', './workflows')

    @staticmethod
    def load_from_mdfile(filename: str, directory = None) -> Workflow:
        """
        Load prompts from a markdown file
        :param filename: The name of the file

        ATTENTION: The markdown file must have the following structure:
        ```markdown
        # Prompts
        ## User [prompt_id]
        [prompt_content]
        ## Assistant [prompt_id]
        [prompt_content]
        ## System [prompt_id]
        [prompt_content]
        ```
        You may have multiple User, Assistant and System sub-sections.

        """
        workflow = Workflow(filename)

        if directory is None:
            directory = os.path.abspath(WorkflowReader.WORKFLOWS_DIR)
        else:
            directory = os.path.abspath(directory)
        abs_file_path = os.path.join(directory, filename)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        section = WorkflowMdSection.NONE
        in_mermaid = False
        in_flowchart = False
        current_content = ''
        current_role = None
        current_key = ''
        for line in content:
            line_strip = line.strip()
            if line_strip.startswith('# '):
                section = WorkflowReader.__check_section(line_strip)
                if section == WorkflowMdSection.NONE:
                    workflow.name = line.replace('# ', '').strip()
                continue

            if section == WorkflowMdSection.NONE:
                if len(line_strip)>0 and line_strip != '\n':
                    workflow.description += line

            if section == WorkflowMdSection.WORKFLOW:
                if line_strip.startswith('```mermaid'):
                    in_mermaid = True
                elif in_mermaid and line_strip.startswith('flowchart'):
                    in_flowchart = True
                elif line_strip.startswith('```'):
                    in_mermaid = False
                    in_flowchart = False
                elif len(line_strip) > 0 and in_mermaid and in_flowchart:
                    WorkflowReader.__parse_flowchart_line(workflow, line_strip)

            if section == WorkflowMdSection.PROMPTS:
                if line_strip.startswith('## User'):
                    if len(current_content) > 0:
                        workflow.prompts[current_key] = Prompt(current_role, current_content)
                        current_content = ''
                    current_role = Prompt.USER
                    current_key = line.replace('## ', '').strip()
                elif line_strip.startswith('## Assistant'):
                    if len(current_content) > 0:
                        workflow.prompts[current_key] = Prompt(current_role, current_content)
                        current_content = ''
                    current_role = Prompt.ASSISTANT
                    current_key = line.replace('## ', '').strip()
                elif line_strip.startswith('## System'):
                    if len(current_content) > 0:
                        workflow.prompts[current_key] = Prompt(current_role, current_content)
                        current_content = ''
                    current_role = Prompt.SYSTEM
                    current_key = line.replace('## ', '').strip()
                else:
                    if current_role is not None:
                        current_content += line
        if len(current_content) > 0:
            if current_key is not None:
                workflow.prompts[current_key] = Prompt(current_role, current_content)

        if workflow.start is None:
            workflow.start = workflow.activities[Activity.Kind.START.name]

        return workflow


    @staticmethod
    def __check_section(line_strip : str) -> WorkflowMdSection:
        if line_strip.startswith('# Workflow'):
            return WorkflowMdSection.WORKFLOW
        if line_strip.startswith('# Prompts'):
            return WorkflowMdSection.PROMPTS
        return WorkflowMdSection.NONE

    @staticmethod
    def __parse_flowchart_line(workflow : Workflow, line : str) -> None:
        # Check if line contains a flow definition (activity -> activity)
        pos = line.find('-->')
        if pos > 0:
            left = line[:pos].strip()
            WorkflowReader.__parse_flowchart_line(workflow, left)
            right = line[pos+3:].strip()
            WorkflowReader.__parse_flowchart_line(workflow, right)
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

            left_activity = workflow.activities[left]
            right_activity = workflow.activities[right]
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
        else:
            # Parse the activity
            activity_name = ''
            activity_expr = ''
            match = re.search(r"(\|.*\|)?\s*([A-Z_]*)[@\{\[]?(.*)?[\}\]]?", line)
            if match is not None:
                activity_name = match.group(2)
                activity_expr = match.group(3)
                if activity_expr.endswith(']') or activity_expr.endswith('}'):
                    activity_expr = activity_expr[:-1]
                # when activity_expr is in additional brackets, remove them
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

            # Create or update activity
            if activity_name not in workflow.activities:
                pos = activity_name.find('_')
                if pos > 0:
                    activity_kindname = activity_name[:pos]
                else:
                    activity_kindname = activity_name

                if activity_kindname == "PARAMS":
                    # Process workflow parameters
                    match = re.search(r'"(.*)"', activity_expr)
                    if not match is None:
                        activity_expr = match.group(1)
                    params = activity_expr.split(',')
                    for param in params:
                        param = param.strip()
                        if len(param) > 0:
                            if param.find('=') > 0:
                                param_key, param_value = param.split('=')
                                workflow.variables[param_key] = param_value
                            else:
                                workflow.variables[param] = ''
                else:
                    # Process activity kind
                    activity_kind = Activity.parse_kind(activity_kindname)
                    if activity_kind is None:
                        raise ValueError(f"Invalid Activity prefix! '{activity_kindname}' " + \
                            "not found in Activity.Kind enumeration.")
                    activity = Activity(activity_kind, activity_name, activity_expr)
                    workflow.activities[activity_name] = activity
            else:
                activity = workflow.activities[activity_name]
                if activity_expr is not None and len(activity_expr) > 0:
                    activity.expression = activity_expr


if __name__ == '__main__':
    MAIN_FILENAME = "sample-project-eval.wf.md"
    main_workflow = WorkflowReader.load_from_mdfile(MAIN_FILENAME)
    print(f"Loaded workflow: {main_workflow.name}")
    print(f"Description: {main_workflow.description}\n")

    print("Loaded variables:")
    for key, value in main_workflow.variables.items():
        print(f"  {key}: {value}")

    print("\nLoaded activities:")
    for key, main_activity in main_workflow.activities.items():
        print(f"  {key}: {main_activity}")

    print("\nLoaded prompts:")
    for key, prompt in main_workflow.prompts.items():
        print(f"  {key}: {prompt}")
