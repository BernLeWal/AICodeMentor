#!/bin/python
"""
The AI-Agent implementation using the Platform OpenAI
"""
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from app.util.string_utils import trunc_middle
from app.agents.agent_config import AIAgentConfig
from app.agents.agent import AIAgent
from app.agents.prompt import Prompt


load_dotenv()
log_level = os.getenv('LOGLEVEL', 'INFO').upper()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=log_level,
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)
# set the loglevel for the OpenAI SDK
logging.getLogger("openai").setLevel(log_level)


# app/agents/AIAgentOpenAI.py
class AIAgentOpenAI(AIAgent):
    """Accesses the OpenAI API, will keep track of the context"""

    def __init__(self, config):
        super().__init__(config)
        logger.info("Creating AIAgentOpenAI with %s", config)

        self.client = OpenAI(
            api_key=config.ai_api_key,
            organization= config.ai_organization_id
        )

        self.model_name = config.ai_model_name
        self.max_prompt_length = config.ai_max_prompt_length


    def system(self, prompt: str) -> str:
        """Starts with a new context (a reset), and provides the chat-systems general behavior"""
        logger.debug("Init AIAgentOpenAI with system prompt: %s", prompt)
        self.messages = []
        return super().system(prompt)

    def ask(self, prompt: str) -> str:
        """Sends a prompt to ChatGPT, will track the result in messages"""
        logger.debug("Ask AIAgentOpenAI: %s", prompt)
        if len(prompt) > self.max_prompt_length:
            prompt = trunc_middle(prompt, self.max_prompt_length)
            logger.warning("Prompt is too long, so truncated in the middle:\n%s", prompt)
        super().ask(prompt)
        messages = [msg.to_dict() for msg in self.messages]
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )
        self.last_result = ""
        for choice in chat_completion.choices:
            self.last_result += choice.message.content + "\n"
        self.messages.append( Prompt(Prompt.ASSISTANT, self.last_result) )
        logger.debug("OpenAI returned: %s", self.last_result)
        return self.last_result


if __name__ == "__main__":
    main_config = AIAgentConfig()
    main_config.load_from_environment()

    main_agent = AIAgentOpenAI(main_config)

    main_agent.system("You are a helpful assistant")
    MAIN_PROMPT = "What is the answer to life, the universe and everything?"
    print(f"User Prompt:\n{MAIN_PROMPT}")
    result = main_agent.ask(MAIN_PROMPT)
    print(f"\nOutput:\n{result}")
