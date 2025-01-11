#!/bin/python
"""
Workflow module
"""

import os
from enum import Enum
from app.agents.prompt import Prompt

# --- app/workflow/workflow.py ---
class Workflow:
    """The base class for all Workflow implementations"""

    class Status(Enum):
        """Workflow status enumeration"""
        CREATED = -1
        DOING = 0
        SUCCESS = 1
        FAILED = 2


    def __init__(self, name: str, interpreter=None, parent=None):
        self.name = name
        self.status : Workflow.Status = Workflow.Status.CREATED
        self.result : str = None
        self.parent : Workflow = parent  # parent workflow
        self.interpreter = interpreter  # WorkflowInterpreter instance
        self.prompts : dict = {}  # prompt_id -> Prompt instance


    def load_from_mdfile(self, filename: str, directory = None):
        """
        Load prompts from a markdown file
        :param filename: The name of the file

        ATTENTION: The markdown file must have the following structure:
        ```markdown
        # Prompts
        ## User [prompt-key]
        [prompt-content]
        ## Assistant [prompt-key]
        [prompt-content]
        ## System [prompt-key]
        [prompt-content]
        ```
        You may have multiple User, Assistant and System sub-sections.

        """
        if directory is None:
            directory = os.path.dirname(__file__)
        else:
            directory = os.path.abspath(directory)
        abs_file_path = os.path.join(directory, filename)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        in_prompts = False
        current_content = ''
        current_role = None
        current_key = ''
        for line in content:
            if in_prompts is False:
                # fast forward to the "# Prompts" section
                if line.startswith('# Prompts'):
                    in_prompts = True
                else:
                    continue
            else:
                # we are in the "# Prompts" section
                line.strip()
                if line.startswith('## User'):
                    if len(current_content) > 0:
                        self.prompts[current_key] = Prompt(current_role, current_content)
                        current_content = ''
                    current_role = Prompt.USER
                    current_key = line.replace('## ', '').strip()
                elif line.startswith('## Assistant'):
                    if len(current_content) > 0:
                        self.prompts[current_key] = Prompt(current_role, current_content)
                        current_content = ''
                    current_role = Prompt.ASSISTANT
                    current_key = line.replace('## ', '').strip()
                elif line.startswith('## System'):
                    if len(current_content) > 0:
                        self.prompts[current_key] = Prompt(current_role, current_content)
                        current_content = ''
                    current_role = Prompt.SYSTEM
                    current_key = line.replace('## ', '').strip()
                else:
                    if current_role is not None:
                        current_content += line
        if len(current_content) > 0:
            self.prompts[current_key] = Prompt(current_role, current_content)


    def __str__(self):
        return f"Workflow(name={self.name}, status={self.status}, result={self.result})"


if __name__ == '__main__':
    main_workflow = Workflow("Check Tool-Chain")
    main_workflow.load_from_mdfile("check-toolchain.wf.md")
    print("Loaded prompts:")
    for key, prompt in main_workflow.prompts.items():
        print(f"  {key}: {prompt}")
