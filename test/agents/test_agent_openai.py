#!/bin/python
"""UnitTests for AIAgentOpenAI"""

import unittest
from app.agents.agent_config import AIAgentConfig
from app.agents.agent_openai_gpt import AIAgentOpenAIGpt


class TestAIAgentOpenAI(unittest.TestCase):
    """UnitTests for AIAgentOpenAI"""
    def setUp(self):
        config = AIAgentConfig("gpt-5-nano")
        self.agent = AIAgentOpenAIGpt(config)


    def test_chat(self):
        """Test setting a system prompt and asking a question"""
        prompt = "You are a helpful assistant"
        self.agent.system(prompt)
        question = "What is the answer to life, the universe and everything?"
        result = self.agent.ask(question)
        print(f"{result}")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
