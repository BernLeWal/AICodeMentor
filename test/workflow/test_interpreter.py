#!/bin/python
"""
UnitTests for WorkflowInterpreter
"""

# --- test/workflow/test_interpreter.py ---
import unittest
from app.agents.agent_factory import AIAgentFactory
from app.commands.shell_executor import ShellCommandExecutor
from app.workflow.activity import Activity
from app.workflow.workflow import Workflow
from app.workflow.workflow_factory import WorkflowFactory
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
        self.assertTrue(interpreter.check_status(Workflow.Status.CREATED))
        interpreter.start()
        self.assertTrue(interpreter.check_status(Workflow.Status.DOING))
        interpreter.success()
        self.assertTrue(interpreter.check_status(Workflow.Status.SUCCESS))
        interpreter.failed()
        self.assertTrue(interpreter.check_status(Workflow.Status.FAILED))

    def test_loop_break(self):
        """Test loop_break method"""
        main_workflow = Workflow(name="Test Workflow loop")
        main_interpreter = WorkflowInterpreter(main_workflow)

        ## hardcoded workflow implementation
        # START
        start = Activity(Activity.Kind.START, "START")
        main_workflow.start = start
        main_workflow.activities[start.name] = start

        # CHECKSTATUS: SUCCESS
        checkstatus_success = Activity(
            Activity.Kind.CHECKSTATUS, "CHECKSTATUS_SUCCESS", "SUCCESS")
        main_workflow.activities[checkstatus_success.name] = checkstatus_success
        start.next = checkstatus_success
        checkstatus_success.next = checkstatus_success

        # FAILED
        failed = Activity(Activity.Kind.FAILED, "FAILED")
        main_workflow.activities[failed.name] = failed
        checkstatus_success.other = failed

        ## run the workflow
        main_status = main_interpreter.run(main_workflow)
        print(f"Workflow completed with {main_status}, Result:\n{main_workflow.result}")
        self.assertEqual(main_status, Workflow.Status.FAILED)


    def test_workflow(self):
        """Test the workflow implementation"""
        main_workflow = WorkflowFactory.load_from_mdfile("check-toolchain.wf.md")
        main_interpreter = WorkflowInterpreter()
        main_interpreter.agent = AIAgentFactory.create_agent()
        main_interpreter.command_executor = ShellCommandExecutor()

        ## run the workflow
        main_status = main_interpreter.run(main_workflow)
        print(f"Workflow completed with {main_status}, Result:\n{main_workflow.result}")
        self.assertEqual(main_status, Workflow.Status.SUCCESS)


if __name__ == "__main__":
    unittest.main()
