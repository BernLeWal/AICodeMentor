#!/bin/python
"""UnitTests for AIAgent"""

import unittest
from app.agents.agent import AIAgent
from app.agents.agent_config import AIAgentConfig
from app.agents.prompt import Prompt

class TestAIAgent(unittest.TestCase):
    """UnitTests for AIAgent"""

    def setUp(self):
        config = AIAgentConfig()
        config.openai_api_key="test_api_key"
        config.openai_organization_id="test_org_id"
        self.agent = AIAgent(config)
        self.agent.model_name = "test_model_name"

    def test_system_prompt(self):
        """Test storing a system prompt"""
        prompt = "You are a helpful assistant"
        result = self.agent.system(prompt)
        self.assertEqual(result, prompt)
        self.assertEqual(len(self.agent.messages), 1)
        self.assertEqual(self.agent.messages[0].role, Prompt.SYSTEM)
        self.assertEqual(self.agent.messages[0].content, prompt)
        self.assertIsNone(self.agent.last_result)

    def test_user_prompt(self):
        """Test storing a user prompt"""
        prompt = "What is the answer to life, the universe and everything?"
        result = self.agent.ask(prompt)
        self.assertEqual(result, prompt)
        self.assertEqual(len(self.agent.messages), 1)
        self.assertEqual(self.agent.messages[0].role, Prompt.USER)
        self.assertEqual(self.agent.messages[0].content, prompt)

    def test_advice_interaction(self):
        """Test storing an advice interaction"""
        question = "What is the answer to life, the universe and everything?"
        answer = "42"
        self.agent.advice(question, answer)
        self.assertEqual(len(self.agent.messages), 2)
        self.assertEqual(self.agent.messages[0].role, Prompt.USER)
        self.assertEqual(self.agent.messages[0].content, question)
        self.assertEqual(self.agent.messages[1].role, Prompt.ASSISTANT)
        self.assertEqual(self.agent.messages[1].content, answer)
        self.assertEqual(self.agent.last_result, answer)

if __name__ == "__main__":
    unittest.main()
