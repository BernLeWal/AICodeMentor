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
from app.agents.agent_google_gemini import AIAgentGoogleGemini
from app.agents.agent_anthropic_claude import AIAgentAnthropicClaude


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)


# app/agents/AIAgentFactory.py
class AIAgentFactory:
    """
    The factory class for creating AI-Agent instances
    """

    @staticmethod
    def create_agent(config:AIAgentConfig = None) -> AIAgent:
        """
        Creates an AI-Agent instance of type AIAgentOpenAI
        """
        if config is None:
            config = AIAgentConfig(config)
        model_name = config.model_name

        # Platform OpenAI Reasoning Models:
        if model_name.startswith("gpt-5"):
            return AIAgentOpenAIInstruct(config)
        elif model_name in ["o1","o3"] or model_name.startswith("o1-") or model_name.startswith("o3-"):
            return AIAgentOpenAIInstruct(config)
        # Platform OpenAI GPT Chat Models:
        elif model_name.startswith("gpt-"):
            return AIAgentOpenAIGpt(config)
        # Google Gemini API Models:
        elif model_name.startswith("gemini-"):
            return AIAgentGoogleGemini(config)
        # Anthropic Claude Models:
        elif model_name.startswith("claude-"):
            return AIAgentAnthropicClaude(config)
        else:
            from app.agents.agent_transformers import AIAgentTransformers
            # Code Llama Models:
            if AIAgentTransformers.is_model_supported(model_name):
                return AIAgentTransformers(config)

        raise ValueError(f"Unsupported model name: {model_name}")


if __name__ == "__main__":
    main_config = AIAgentConfig("gpt-5-mini") # use "codellama/CodeLlama-7b-Instruct-hf" to test the transformers agent
    main_agent = AIAgentFactory.create_agent(main_config)
    print(f"Type of agent is {type(main_agent)}")
    system = PromptFactory.load("prep-agent.system.prompt.md")[0].content
    main_agent.system(system)
    QUESTION = "Check if in the shell the git commands are installed correctly " +\
        "and if the github-server (https://www.github.com) is reachable via network."
    result = main_agent.ask(QUESTION)
    print(f"{result}")
