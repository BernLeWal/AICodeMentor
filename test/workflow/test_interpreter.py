#!/bin/python
"""
UnitTests for WorkflowInterpreter
"""

# --- test/workflow/test_interpreter.py ---
import unittest
from app.workflow.activity import Activity
from app.workflow.context import Context
from app.workflow.workflow import Workflow
from app.workflow.interpreter import WorkflowInterpreter


class TestWorkflowInterpreter(unittest.TestCase):
    """UnitTests for WorkflowInterpreter"""

    def test_interpreter_initialization(self):
        """Test WorkflowInterpreter initialization"""
        parent_interpreter = WorkflowInterpreter(None, None)
        self.assertTrue(len(parent_interpreter.id)>=15)

        child_interpreter = WorkflowInterpreter(None, None, parent_interpreter)
        self.assertEqual(child_interpreter.parent_interpreter.id, parent_interpreter.id)


    def test_loop_break(self):
        """Test loop_break method"""
        main_workflow = Workflow("Test Workflow loop")

        ## hardcoded workflow implementation
        # START
        start = Activity(Activity.Kind.START, "START")
        main_workflow.start = start
        main_workflow.activities[start.name] = start

        # CHECKS: SUCCESS
        checkstatus_success = Activity(
            Activity.Kind.CHECK, "CHECK_SUCCESS", "STATUS == SUCCESS")
        main_workflow.activities[checkstatus_success.name] = checkstatus_success
        start.next = checkstatus_success
        checkstatus_success.next = checkstatus_success

        # FAILED
        failed = Activity(Activity.Kind.FAILED, "FAILED")
        main_workflow.activities[failed.name] = failed
        checkstatus_success.other = failed

        ## run the workflow
        main_interpreter = WorkflowInterpreter(main_workflow)
        main_context = Context(main_workflow, None, None)
        (main_status, main_result) = main_interpreter.run(main_context)
        print(f"Workflow completed with {main_status}, Result:\n{main_result}")
        self.assertEqual(main_status, Workflow.Status.FAILED)


if __name__ == "__main__":
    unittest.main()
