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

        # CHECK_STATUS: SUCCESS
        checkstatus_success = Activity(
            Activity.Kind.CHECK_STATUS, "CHECK_STATUS_SUCCESS", "SUCCESS")
        main_workflow.activities[checkstatus_success.name] = checkstatus_success
        start.next = checkstatus_success
        checkstatus_success.next = start

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
        main_workflow.name = "Test build toolchain"
        main_interpreter = WorkflowInterpreter()
        main_interpreter.agent = AIAgentFactory.create_agent()
        main_interpreter.command_executor = ShellCommandExecutor()

        ## hardcoded workflow implementation

        # START
        start = Activity(Activity.Kind.START, "START")
        main_workflow.start = start
        main_workflow.activities[start.name] = start

        # PROMPT: System
        prompt_system = Activity(Activity.Kind.PROMPT, "PROMPT_SYSTEM", "System")
        main_workflow.activities[prompt_system.name] = prompt_system
        start.next = prompt_system

        # PROMPT: User TestGit
        prompt_testgit = Activity(Activity.Kind.PROMPT, "PROMPT_TESTGIT", "User TestGit")
        main_workflow.activities[prompt_testgit.name] = prompt_testgit
        prompt_system.next = prompt_testgit

        # EXECUTE: ShellCommands
        execute_output = Activity(Activity.Kind.EXECUTE, "EXECUTE_OUTPUT")
        main_workflow.activities[execute_output.name] = execute_output
        prompt_testgit.next = execute_output

        # PROMPT: User CommandResults
        prompt_cmdresults = Activity(
            Activity.Kind.PROMPT, "PROMPT_CMDRESULTS", "User CommandResults")
        main_workflow.activities[prompt_cmdresults.name] = prompt_cmdresults
        execute_output.next = prompt_cmdresults

        # CHECK_STATUS: SUCCESS
        checkresult_success = Activity(
            Activity.Kind.CHECK_RESULT, "CHECK_RESULT_SUCCESS", "SUCCESS")
        main_workflow.activities[checkresult_success.name] = checkresult_success
        prompt_cmdresults.next = checkresult_success

        # PROMT: User SuccessSummary
        prompt_successsummary = Activity(
            Activity.Kind.PROMPT, "PROMPT_SUCCESS_SUMMARY", "User SuccessSummary")
        main_workflow.activities[prompt_successsummary.name] = prompt_successsummary
        checkresult_success.next = prompt_successsummary

        # SUCCESS
        success = Activity(Activity.Kind.SUCCESS, "SUCCESS")
        main_workflow.activities[success.name] = success
        prompt_successsummary.next = success

        # CHECK_STATUS: FAILED
        checkresult_failed = Activity(Activity.Kind.CHECK_RESULT, "CHECK_RESULT_FAILED", "FAILED")
        main_workflow.activities[checkresult_failed.name] = checkresult_failed
        checkresult_success.other = checkresult_failed

        # PROMT: User FailedSummary
        prompt_failedsummary = Activity(
            Activity.Kind.PROMPT, "PROMPT_FAILED_SUMMARY", "User FailedSummary")
        main_workflow.activities[prompt_failedsummary.name] = prompt_failedsummary
        checkresult_failed.next = prompt_failedsummary

        # FAILED
        failed = Activity(Activity.Kind.FAILED, "FAILED")
        main_workflow.activities[failed.name] = failed
        prompt_failedsummary.next = failed

        # PROMPT: Improve
        prompt_improve = Activity(Activity.Kind.PROMPT, "PROMPT_IMPROVE", "User Improve")
        main_workflow.activities[prompt_improve.name] = prompt_improve
        failed.other = prompt_improve
        prompt_improve.next = execute_output
        checkresult_failed.other = prompt_improve


        ## run the workflow
        main_status = main_interpreter.run(main_workflow)
        print(f"Workflow completed with {main_status}, Result:\n{main_workflow.result}")
        self.assertEqual(main_status, Workflow.Status.SUCCESS)


if __name__ == "__main__":
    unittest.main()
