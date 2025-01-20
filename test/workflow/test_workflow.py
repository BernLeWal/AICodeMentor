#!/bin/python
"""
UnitTests for Workflow
"""

# --- test/workflow/test_workflow.py ---
import unittest
from app.workflow.workflow import Workflow
from app.workflow.workflow_reader import WorkflowReader

class TestWorkflow(unittest.TestCase):
    """UnitTests for Workflow"""

    def test_workflow_initialization(self):
        """Test Workflow initialization"""
        workflow = Workflow("Test Workflow")
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.status, Workflow.Status.CREATED)
        self.assertEqual(workflow.result, None)


    def test_workflow_load_from_mdfile(self):
        """Test Workflow load_from_mdfile method"""
        workflow = WorkflowReader.load_from_mdfile("check-toolchain.wf.md")
        self.assertEqual(workflow.name, "Check Toolchain")
        self.assertEqual(workflow.status, Workflow.Status.CREATED)
        self.assertEqual(workflow.result, None)

        print(f"Loaded workflow: {workflow.name}")
        print(f"Description: {workflow.description}\n")
        print("Loaded variables:")
        for key, value in workflow.variables.items():
            print(f"  {key}: {value}")
        print("Loaded activities:")
        for key, activity in workflow.activities.items():
            print(f"  {key}: {activity}")
        print("\nLoaded prompts:")
        for key, prompt in workflow.prompts.items():
            print(f"  {key}: {prompt}")

        # assert if the workflow.prompts has a "System" key
        self.assertTrue("System" in workflow.prompts)


if __name__ == "__main__":
    unittest.main()
