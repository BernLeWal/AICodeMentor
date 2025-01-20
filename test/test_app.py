#!/bin/python
"""Integration-Tests"""


import unittest
from app.agents.agent_factory import AIAgentFactory
from app.commands.shell_executor import ShellCommandExecutor
from app.workflow.workflow import Workflow
from app.workflow.workflow_reader import WorkflowReader
from app.workflow.interpreter import WorkflowInterpreter



class TestAll(unittest.TestCase):
    """Integration-Tests for the app"""
    def setUp(self):
        pass


    def test_workflow(self):
        """Test the workflow implementation"""
        main_workflow = WorkflowReader.load_from_mdfile("check-toolchain.wf.md")
        main_interpreter = WorkflowInterpreter()
        main_interpreter.agent = AIAgentFactory.create_agent()
        main_interpreter.command_executor = ShellCommandExecutor()

        ## run the workflow
        main_status = main_interpreter.run(main_workflow)
        print(f"Workflow completed with {main_status}, Result:\n{main_workflow.result}")
        self.assertEqual(main_status, Workflow.Status.SUCCESS)


if __name__ == "__main__":
    unittest.main()
