#!/bin/python
"""
WorkflowFactory module  - Factory for Workflow instances
"""

import os
from app.agents.prompt import Prompt
from app.workflow.workflow import Workflow


class WorkflowFactory:
    """The base class for all WorkflowFactory implementations"""

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
            if in_prompts:
                # we are in the "# Prompts" section
                line_strip = line.strip()
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
            workflow.prompts[current_key] = Prompt(current_role, current_content)

        return workflow


if __name__ == '__main__':
    main_workflow = WorkflowFactory.load_from_mdfile("check-toolchain.wf.md")
    main_workflow.name = "Check Tool-Chain"
    print("Loaded prompts:")
    for key, prompt in main_workflow.prompts.items():
        print(f"  {key}: {prompt}")
