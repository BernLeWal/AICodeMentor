#!/bin/python
"""UnitTests for AIAgentFactory"""

import unittest
from app.agents.prompt_factory import PromptFactory
from app.agents.agent_factory import AIAgentFactory


class TestAIAgentFactory(unittest.TestCase):
    """UnitTests for AIAgentFactory"""

    def test_chat(self):
        """Test setting a system prompt and asking a question"""
        agent = AIAgentFactory.create_agent()
        self.assertIsNotNone(agent)
        system = PromptFactory.load("prep-agent.system.prompt.md")[0].content
        agent.system(system)
        question = "Check if in the shell the git commands are installed correctly " +\
            "and if the github-server (https://www.github.com) is reachable via network."
        result = agent.ask(question)
        print(f"{result}")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
