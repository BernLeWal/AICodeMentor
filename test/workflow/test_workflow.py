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
        self.assertEqual(workflow.status, Workflow.DOING)
        self.assertEqual(workflow.result, None)


if __name__ == "__main__":
    unittest.main()
