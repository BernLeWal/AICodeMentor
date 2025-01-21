#!/bin/python
"""
The factory class for creating AI-Agent instances
"""
import logging
import os
from dotenv import load_dotenv
from app.agents.prompt_factory import PromptFactory
from app.agents.agent_config import AIAgentConfig
from app.agents.agent import AIAgent
from app.agents.agent_openai import AIAgentOpenAI


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
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



if __name__ == "__main__":
    main_agent = AIAgentFactory.create_agent()
    system = PromptFactory.load("prep-agent.system.prompt.md")[0].content
    main_agent.system(system)
    QUESTION = "Check if in the shell the git commands are installed correctly " +\
        "and if the github-server (https://www.github.com) is reachable via network."
    result = main_agent.ask(QUESTION)
    print(f"{result}")
