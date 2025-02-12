#!/bin/python
"""
UnitTests for ActivityInterpreter
"""

import unittest
from app.agents.agent_config import AIAgentConfig
from app.agents.prompt import Prompt
from app.workflow.activity import Activity
from app.workflow.workflow import Workflow
from app.workflow.context import Context
from app.workflow.activity_interpreter import ActivityInterpreter

class TestActivityInterpreter(unittest.TestCase):
    """UnitTests for ActivityInterpreter"""


    def test_assign(self):
        """Test ASSIGN activity"""
        context = Context( Workflow("Test Workflow") )
        interpreter = ActivityInterpreter(context)

        activity = Activity(Activity.Kind.ASSIGN, "ASSIGN", "'hello'")
        activity.accept(interpreter)

        # Internal variable
        self.assertEqual(context.get_value(Context.InternalVariable.RESULT.name),
            "hello")
        # Environment variable
        self.assertTrue(context.get_value("SHELL").find("bash") >= 0)


    def test_set(self):
        """Test SET activity"""
        context = Context( Workflow("Test Workflow") )
        interpreter = ActivityInterpreter(context)

        activity = Activity(Activity.Kind.SET, "SET", "foo='bar'")
        activity.accept(interpreter)

        self.assertEqual(context.get_value("foo"), "bar")


    def test_check_status(self):
        """Test CHECK activity with STATUS expressions"""
        context = Context( Workflow("Test Workflow") )
        interpreter = ActivityInterpreter(context)

        activity1 = Activity(Activity.Kind.CHECK, "CHECK_CREATED", "STATUS == 'CREATED'")
        activity1.accept(interpreter)
        self.assertTrue(interpreter.activity_succeeded)

        interpreter.visit_start(None)
        activity2 = Activity(Activity.Kind.CHECK, "CHECK_DOING", "STATUS equals 'DOING'")
        activity2.accept(interpreter)
        self.assertTrue(interpreter.activity_succeeded)

        interpreter.success()
        activity3 = Activity(Activity.Kind.CHECK, "CHECK_SUCCESS", "STATUS contains SUCCESS")
        activity3.accept(interpreter)
        self.assertTrue(interpreter.activity_succeeded)

        interpreter.failed()
        activity4 = Activity(Activity.Kind.CHECK, "CHECK_FAILED", "STATUS matches FAILED")
        activity4.accept(interpreter)
        self.assertTrue(interpreter.activity_succeeded)


    def test_prompt(self):
        """Test prompt method"""
        workflow = Workflow("Test Workflow prompt")
        workflow.prompts["System"] = Prompt(Prompt.SYSTEM, "A system prompt")
        workflow.prompts["User Name"] = \
            Prompt(Prompt.USER, "Just echo the following string:A user prompt")
        context = Context( workflow )
        interpreter = ActivityInterpreter(context )
        config = AIAgentConfig()
        config.load_from_environment()

        activity1 = Activity(Activity.Kind.PROMPT, "PROMPT_SYSTEM", "System")
        activity1.accept(interpreter)
        self.assertEqual(context.result, "")   # system prompt returns empty string

        activity2 = Activity(Activity.Kind.PROMPT, "PROMPT_USER", "User Name")
        activity2.accept(interpreter)
        self.assertEqual(context.result.strip(), "A user prompt")



if __name__ == "__main__":
    unittest.main()
