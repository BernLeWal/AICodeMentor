#!/bin/python
"""
The base class for all AI Agent implementations
"""
import logging
import os
from dotenv import load_dotenv
from app.agents.agent_config import AIAgentConfig
from app.agents.prompt import Prompt


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


# app/agents/AIAgent.py
class AIAgent:
    """The base class for all AI Agent implementations"""
    def __init__(self, config: AIAgentConfig):
        logger.debug("Initializing AIAgent with config: %s", config)
        self.config : AIAgentConfig = config

        # common LLM configs
        self.model_name:str = os.getenv('AI_MODEL_NAME', 'gpt-4o-mini') # LLM model used
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))       # output randomness
        self.top_p = float(os.getenv('AI_TOP_P', '1.0'))                   # nucleus sampling
        self.frequency_penalty = float(os.getenv('AI_FREQUENCY_PENALTY', '0.0'))
        self.presence_penalty = float(os.getenv('AI_PRESENCE_PENALTY', '0.0'))
        self.max_output_tokens = int(os.getenv("AI_MAX_OUTPUT_TOKENS", '1024'))
        stop_seq:str = os.getenv('AI_STOP_SEQUENCE', None)     # stop gen. at this seq.
        self.stop_sequences = stop_seq.split('|') if stop_seq else None

        # further processing configs
        self.max_prompt_length = int(os.getenv('AI_MAX_PROMPT_LENGTH', '2000'))


        self.messages : list = []
        self.last_result : str = None

    def system(self, prompt: str) -> str:
        """Store the system prompt"""
        logger.debug("System prompt received: %s", prompt)
        self.messages.append( Prompt(Prompt.SYSTEM, prompt) )
        self.last_result = None
        return prompt

    def ask(self, prompt: str) -> str:
        """Store the user prompt"""
        logger.debug("User prompt received: %s", prompt)
        self.messages.append( Prompt(Prompt.USER, prompt) )
        # self.last_result has to be set by the implementation
        return prompt

    def advice(self, question: str, answer: str):
        """Store the advice interaction"""
        logger.debug("Advice interaction - Question: %s, Answer: %s", question, answer)
        if not question is None:
            self.messages.append( Prompt(Prompt.USER, question) )
        if not answer is None:
            self.messages.append( Prompt(Prompt.ASSISTANT, answer) )
        self.last_result = answer

    def answer(self, answer: str):
        """Store the answer of the AIAgent"""
        logger.debug("AIAgent's Answer: %s", answer)
        if not answer is None:
            self.messages.append( Prompt(Prompt.ASSISTANT, answer) )
        self.last_result = answer


if __name__ == "__main__":
    main_config = AIAgentConfig()
    main_config.load_from_environment()

    main_agent = AIAgent(main_config)

    print("System Prompt:")
    main_agent.system("You are a helpful assistant")
    for message in main_agent.messages:
        print(f"  - {message.role}: {message.content}")

    print("User Prompt:")
    main_agent.ask("What is the answer to life, the universe and everything?")
    for message in main_agent.messages:
        print(f"  - {message.role}: {message.content}")

    print("Assistant Prompt:")
    main_agent.advice(None, "42")
    for message in main_agent.messages:
        print(f"  - {message.role}: {message.content}")
