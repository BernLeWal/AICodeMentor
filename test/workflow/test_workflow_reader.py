#!/bin/python
"""
UnitTests for Workflow
"""

# --- test/workflow/test_workflow.py ---
import unittest
from app.workflow.workflow import Workflow
from app.workflow.reader import WorkflowReader

class TestWorkflow(unittest.TestCase):
    """UnitTests for Workflow"""

    def test_workflow_initialization(self):
        """Test Workflow initialization"""
        workflow = Workflow("Test Workflow")
        self.assertEqual(workflow.name, "Test Workflow")


    def test_workflow_load_from_mdfile(self):
        """Test Workflow load_from_mdfile method"""
        workflow = WorkflowReader.load_from_mdfile("check-toolchain.wf.md")

        print(f"Loaded workflow: {workflow.name}")
        self.assertEqual(workflow.name, "Check Toolchain")

        print(f"Description: {workflow.description}\n")
        self.assertTrue(len(workflow.description)>0)

        print("Loaded parameters:")
        for key, value in workflow.params.items():
            print(f"  {key}: {value}")
        self.assertEqual(len(workflow.params), 1)

        print("Loaded activities:")
        for key, activity in workflow.activities.items():
            print(f"  {key}: {activity}")
        self.assertEqual(len(workflow.activities), 10)

        print("\nLoaded prompts:")
        for key, prompt in workflow.prompts.items():
            print(f"  {key}: {prompt}")
        self.assertEqual(len(workflow.prompts), 4)
        self.assertTrue("System" in workflow.prompts)

        print(f"\nStart activity:      {workflow.start}")
        self.assertIsNotNone(workflow.start)

        print(f"On_Success activity: {workflow.on_success}")
        self.assertIsNone(workflow.on_success)

        print(f"On_Failed activity:  {workflow.on_failed}")
        self.assertIsNone(workflow.on_failed)
        

if __name__ == "__main__":
    unittest.main()
