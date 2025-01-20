#!/bin/python
"""
UnitTests for WorkflowInterpreter
"""

# --- test/workflow/test_interpreter.py ---
import unittest
from app.agents.agent import AIAgent
from app.agents.agent_config import AIAgentConfig
from app.agents.prompt import Prompt
from app.workflow.activity import Activity
from app.workflow.workflow import Workflow
from app.workflow.interpreter import WorkflowInterpreter


class TestWorkflowInterpreter(unittest.TestCase):
    """UnitTests for WorkflowInterpreter"""

    def test_interpreter_initialization(self):
        """Test WorkflowInterpreter initialization"""
        workflow = Workflow("Test Workflow")
        interpreter = WorkflowInterpreter(workflow)
        self.assertEqual(interpreter.workflow.name, "Test Workflow")

    def test_assign(self):
        """Test assign method"""
        workflow = Workflow("Test Workflow")
        interpreter = WorkflowInterpreter(workflow)
        interpreter.assign("'hello'")
        # Internal variable
        self.assertEqual(interpreter.get_value(WorkflowInterpreter.InternalVariable.RESULT.name),
            "hello")
        # Environment variable
        self.assertTrue(interpreter.get_value("SHELL").find("bash") >= 0)

    def test_set(self):
        """Test set method"""
        workflow = Workflow("Test Workflow")
        interpreter = WorkflowInterpreter(workflow)
        interpreter.set("foo='bar'")
        self.assertEqual(interpreter.get_value("foo"), "bar")

    def test_check_status(self):
        """Test check_status method"""
        workflow = Workflow("Test Workflow")
        interpreter = WorkflowInterpreter(workflow)
        self.assertTrue(interpreter.check("STATUS == 'CREATED'"))
        interpreter.start()
        self.assertTrue(interpreter.check("STATUS equals 'DOING'"))
        interpreter.success()
        self.assertTrue(interpreter.check("STATUS contains SUCCESS"))
        interpreter.failed()
        self.assertTrue(interpreter.check("STATUS matches FAILED"))

    def test_prompt(self):
        """Test prompt method"""
        config = AIAgentConfig()
        config.load_from_environment()
        workflow = Workflow("Test Workflow prompt")
        workflow.prompts["System"] = Prompt(Prompt.SYSTEM, "A system prompt")
        workflow.prompts["User Name"] = Prompt(Prompt.USER, "Just echo the following string:A user prompt")
        interpreter = WorkflowInterpreter(workflow)
        interpreter.prompt(prompt_id="System")
        self.assertEqual(workflow.result, "")   # system prompt returns empty string
        interpreter.prompt(prompt_id="User Name")
        self.assertEqual(workflow.result.strip(), "A user prompt")

    def test_loop_break(self):
        """Test loop_break method"""
        main_workflow = Workflow("Test Workflow loop")
        main_interpreter = WorkflowInterpreter(main_workflow)

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
        main_status = main_interpreter.run(main_workflow)
        print(f"Workflow completed with {main_status}, Result:\n{main_workflow.result}")
        self.assertEqual(main_status, Workflow.Status.FAILED)


if __name__ == "__main__":
    unittest.main()
