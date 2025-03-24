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
from app.agents.agent_openai_gpt import AIAgentOpenAIGpt
from app.agents.agent_openai_instruct import AIAgentOpenAIInstruct


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
    def create_agent(model_name:str = None) -> AIAgent:
        """
        Creates an AI-Agent instance of type AIAgentOpenAI
        """
        if model_name is None:
            model_name = os.getenv('AI_MODEL_NAME', 'gpt-4o-mini')
        logger.debug("Creating agent for model: %s", model_name)

        config = AIAgentConfig()
        config.load_from_environment()

        # Platform OpenAI GPT Chat Models:
        if model_name.startswith("gpt-"):
            return AIAgentOpenAIGpt(config)
        # Platform OpenAI Reasoning Models (o1/o3):
        elif model_name.startswith("o1-") or model_name.startswith("o3-"):
            return AIAgentOpenAIInstruct(config)

        raise ValueError(f"Unsupported model name: {model_name}")


    @staticmethod
    def get_model_name() -> str:
        """
        Returns the model name of the AI-Agent instance
        """
        return os.getenv('AI_MODEL_NAME', 'gpt-4o-mini')


if __name__ == "__main__":
    main_agent = AIAgentFactory.create_agent()
    system = PromptFactory.load("prep-agent.system.prompt.md")[0].content
    main_agent.system(system)
    QUESTION = "Check if in the shell the git commands are installed correctly " +\
        "and if the github-server (https://www.github.com) is reachable via network."
    result = main_agent.ask(QUESTION)
    print(f"{result}")
