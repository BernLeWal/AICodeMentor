#!/bin/python
"""UnitTests for AIAgentFactory"""

import unittest
from app.agents.prompt_factory import PromptFactory
from app.agents.agent_factory import AIAgentFactory


class TestAIAgentFactory(unittest.TestCase):
    """UnitTests for AIAgentFactory"""

    def test_chat(self):
        """Test setting a system prompt and asking a question"""
        agent = AIAgentFactory.create_preparation_agent()
        self.assertIsNotNone(agent)
        question = PromptFactory.load("prep-agent.test-git.prompt.md")[0].content
        result = agent.ask(question)
        print(f"{result}")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
