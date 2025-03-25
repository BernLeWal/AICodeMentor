#!/bin/python
"""
The AI-Agent implementation using the Platform OpenAI Instruct Models (o1/o3)
"""
import logging
import os
import time
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
class AIAgentOpenAIInstruct(AIAgent):
    """Accesses the OpenAI API, will keep track of the context"""

    def __init__(self, config):
        super().__init__(config)
        logger.info("Creating AIAgentOpenAI with %s", config)

        self.client = OpenAI(
            api_key=config.ai_api_key,
            organization= config.ai_organization_id
        )


    def system(self, prompt: str) -> str:
        """Starts with a new context (a reset), and provides the chat-systems general behavior"""
        logger.debug("Init AIAgentOpenAI with system prompt: %s", prompt)
        self.messages = []
        super().system(prompt)
        logger.warning("Instruct models do not support System propmts! Ignoring: %s", prompt)
        self.messages = []
        return ""

    def ask(self, prompt: str) -> str:
        """Sends a prompt to ChatGPT, will track the result in messages"""
        logger.debug("Ask AIAgentOpenAI: %s", prompt)
        if len(prompt) > self.max_prompt_length:
            prompt = trunc_middle(prompt, self.max_prompt_length)
            logger.warning("Prompt is too long, so truncated in the middle:\n%s", prompt)
        super().ask(prompt)

        messages = [msg.to_dict() for msg in self.messages]

        start_time = time.perf_counter()
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            #temperature=self.temperature  # not supported on instruct models!
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            max_completion_tokens=self.max_output_tokens,
            stop=self.stop_sequences
        )
        self.total_duration_sec += time.perf_counter() - start_time

        self.last_result = ""
        for choice in chat_completion.choices:
            self.last_result += choice.message.content + "\n"
        self.messages.append( Prompt(Prompt.ASSISTANT, self.last_result) )
        # record telemetry
        self.total_iterations = len(self.messages)
        self.total_completion_chars += len(self.last_result)
        self.total_chars += len(self.last_result)
        usage = chat_completion.usage
        self.total_prompt_tokens = usage.prompt_tokens
        self.total_completion_tokens = usage.completion_tokens
        self.total_tokens = usage.total_tokens

        logger.debug("OpenAI returned: %s", self.last_result)
        return self.last_result


if __name__ == "__main__":
    main_config = AIAgentConfig()
    main_config.load_from_environment()

    main_agent = AIAgentOpenAIInstruct(main_config)

    main_agent.system("You are a helpful assistant")
    MAIN_PROMPT = "What is the answer to life, the universe and everything?"
    print(f"User Prompt:\n{MAIN_PROMPT}")
    result = main_agent.ask(MAIN_PROMPT)
    print(f"\nOutput:\n{result}")
