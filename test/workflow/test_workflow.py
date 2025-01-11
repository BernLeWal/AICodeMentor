#!/bin/python
"""
UnitTests for Workflow
"""

# --- test/workflow/test_workflow.py ---
import unittest
from app.workflow.workflow import Workflow

class TestWorkflow(unittest.TestCase):
    """UnitTests for Workflow"""

    def test_workflow_initialization(self):
        """Test Workflow initialization"""
        workflow = Workflow(name="Test Workflow")
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.status, Workflow.Status.CREATED)
        self.assertEqual(workflow.result, None)


    def test_workflow_load_from_mdfile(self):
        """Test Workflow load_from_mdfile method"""
        workflow = Workflow(name="Test Workflow")
        workflow.load_from_mdfile("check-toolchain.wf.md", directory="app/workflow")
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.status, Workflow.Status.CREATED)
        self.assertEqual(workflow.result, None)
        # assert if the workflow.prompts has a "System" key
        print("Loaded prompts from check-toolchain.wf.md file:")
        for key, prompt in workflow.prompts.items():
            print(f"  {key}: {prompt}")        
        self.assertTrue("System" in workflow.prompts)

if __name__ == "__main__":
    unittest.main()
