#!/bin/python
"""
The factory class for creating AI-Agent instances
"""
import logging
from app.agents.prompt_factory import PromptFactory
from app.agents.agent_config import AIAgentConfig
from app.agents.agent import AIAgent
from app.agents.agent_openai import AIAgentOpenAI


# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# app/agents/AIAgentFactory.py
class AIAgentFactory:
    """
    The factory class for creating AI-Agent instances
    """

    @staticmethod
    def create_agent() -> AIAgent:
        """
        Creates an AI-Agent instance of type AIAgentOpenAI
        """
        logger.debug("Creating agent")
        config = AIAgentConfig()
        config.load_from_environment()
        agent = AIAgentOpenAI(config)
        return agent


    @staticmethod
    def create_preparation_agent() -> AIAgent:
        """
        Creates an AI-Agent instance of type AIAgentOpenAI 
        for the preparation of student sourcecode submissions.
        """
        logger.debug("Creating preparation-agent")
        config = AIAgentConfig()
        config.load_from_environment()
        agent = AIAgentOpenAI(config)
        agent.messages = PromptFactory.load("prep-agent.system.prompt.md")
        return agent


if __name__ == "__main__":
    main_agent = AIAgentFactory.create_preparation_agent()
    question = PromptFactory.load("prep-agent.test-git.prompt.md")[0].content
    result = main_agent.ask(question)
    print(f"{result}")
