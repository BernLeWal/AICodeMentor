#!/bin/python


# --- test/workflow/test_interpreter.py ---
import unittest
from app.workflow.workflow import Workflow
from app.workflow.interpreter import WorkflowInterpreter


class TestWorkflowInterpreter(unittest.TestCase):
    """UnitTests for WorkflowInterpreter"""

    def test_interpreter_initialization(self):
        """Test WorkflowInterpreter initialization"""
        workflow = Workflow(name="Test Workflow")
        interpreter = WorkflowInterpreter(workflow)
        self.assertEqual(interpreter.workflow.name, "Test Workflow")

    def test_check_status(self):
        """Test check_status method"""
        workflow = Workflow(name="Test Workflow")
        interpreter = WorkflowInterpreter(workflow)
        self.assertTrue(interpreter.check_status(Workflow.DOING))


if __name__ == "__main__":
    unittest.main()
