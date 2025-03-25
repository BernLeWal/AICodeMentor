#!/bin/python
"""
WorkflowRunner class to run the AI CodeMentor Workflow
"""

import datetime
from app.workflow.workflow import Workflow
from app.workflow.workflow_reader import WorkflowReader
from app.workflow.interpreter import WorkflowInterpreter
from app.workflow.context import Context
from app.agents.agent_factory import AIAgentFactory
from app.commands.shell_executor import ShellCommandExecutor
from app.agents.agent_config import AIAgentConfig

class WorkflowRunner:
    """
    WorkflowRunner class to run the AI CodeMentor Workflow
    """
    def __init__(self, workflow_file, key_values):
        self.workflow_file = workflow_file
        self.key_values = key_values

        self.start_time = None
        self.duration_sec = 0

        self.context:Context = None


    def run(self) -> tuple[Workflow.Status, str]:
        """
        Run the AI CodeMentor Workflow
        """
        self.start_time = datetime.datetime.now()
        main_workflow = WorkflowReader().load_from_mdfile(self.workflow_file, ".")
        print(f"Running workflow: {main_workflow.name} (from file {main_workflow.filepath}) "+\
            f"using AI-model {AIAgentConfig.get_model_name()} ")
        if self.key_values:
            print("with parameters:")
            for kv in self.key_values:
                key, value = kv.split("=")
                print(f"  - {key}={value}\n")
                main_workflow.params[key] = value

        main_interpreter = WorkflowInterpreter(main_workflow)

        ## run the workflow
        self.context = Context(main_workflow, AIAgentFactory.create_agent(), ShellCommandExecutor())
        results = main_interpreter.run(self.context)
        self.duration_sec = (datetime.datetime.now() - self.start_time).total_seconds()
        return results


    def get_agent(self):
        """Returns the agent used in the workflow"""
        if not self.context:
            return None
        return self.context.agent
