#!/bin/python
"""
UnitTests for WorkflowInterpreter
"""

# --- test/workflow/test_interpreter.py ---
import unittest
from app.agents.prompt import Prompt
from app.commands.shell_executor import ShellCommandExecutor
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
        self.assertTrue(interpreter.check_status(Workflow.Status.CREATED))
        interpreter.start()
        self.assertTrue(interpreter.check_status(Workflow.Status.DOING))
        interpreter.success()
        self.assertTrue(interpreter.check_status(Workflow.Status.SUCCESS))
        interpreter.failed()
        self.assertTrue(interpreter.check_status(Workflow.Status.FAILED))

    def test_workflow(self):
        """Test the workflow implementation"""
        main_workflow = Workflow(name="Test build toolchain")
        main_interpreter = WorkflowInterpreter(main_workflow)
        main_interpreter.command_executor = ShellCommandExecutor()

        ## hardcoded workflow implementation
        # START
        main_interpreter.start()  # no input required

        # PROMPT: System
        main_interpreter.prompt(
            Prompt.SYSTEM,
            prompt_file="prep-agent.system.prompt.md")

        # PROMPT: User TestGit
        main_interpreter.prompt(
            Prompt.USER,
            prompt_file="prep-agent.test-git.prompt.md")

        iteration = 1
        while iteration < 3:

            # EXECUTE: ShellCommands
            main_interpreter.execute()

            # PROMPT: User CommandResults
            main_interpreter.prompt(
                Prompt.USER,
                prompt_file="prep-agent.test-git-results.prompt.md",
                append_results=True)

            # CHECK_STATUS: SUCCESS
            if main_interpreter.check_result("SUCCESS"):

                # PROMT: User SuccessSummary
                main_interpreter.prompt(
                    Prompt.USER,
                    prompt_file="prep-agent.test-git-success.prompt.md")

                # SUCCESS
                main_interpreter.success()
                print(main_interpreter.workflow.result)
                break

            if main_interpreter.check_result("FAILED"):

                # PROMT: User FailedSummary
                main_interpreter.prompt(
                    Prompt.USER,
                    prompt_file="prep-agent.test-git-failed.prompt.md")

                # FAILED
                main_interpreter.failed()
                print(main_interpreter.workflow.result)
                break

            # PROMPT: Improve
            main_interpreter.prompt(
                Prompt.USER,
                prompt_file="prep-agent.test-git-improve.prompt.md")
            iteration += 1

        self.assertEqual(main_interpreter.workflow.status, Workflow.Status.SUCCESS)


if __name__ == "__main__":
    unittest.main()
