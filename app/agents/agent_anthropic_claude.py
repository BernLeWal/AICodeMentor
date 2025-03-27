#!/bin/python
"""
The AI-Agent implementation using the Claude models from Anthropic
"""
import logging
import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic
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
# set the loglevel for the Anthropic SDK
logging.getLogger("anthropic").setLevel(log_level)


class AIAgentAnthropicClaude(AIAgent):
    """Accesses the Anthropic Claude API and keeps track of the context"""

    def __init__(self, config):
        super().__init__(config)
        logger.info("Creating AIAgentAnthropicClaude with %s", config)

        self.client = Anthropic(
            api_key=config.anthropic_api_key,
        )


    def system(self, prompt: str) -> str:
        """
        Initializes the system with a prompt; 
        in Claude this is prepended in the first message.
        """
        logger.debug("Init AIAgentAnthropicClaude with system prompt: %s", prompt)
        self.messages = []
        return super().system(prompt)


    def ask(self, prompt: str) -> str:
        """Sends a prompt to Claude, tracks message history and usage"""
        logger.debug("Ask AIAgentAnthropicClaude: %s", prompt)
        if len(prompt) > self.max_prompt_length:
            prompt = trunc_middle(prompt, self.max_prompt_length)
            logger.warning("Prompt is too long, so truncated in the middle:\n%s", prompt)
        super().ask(prompt)

        system_prompt = self.messages[0].content if len(self.messages) > 0 else None
        claude_messages = [msg.to_dict() for msg in self.messages[1::]]

        start_time = time.perf_counter()
        response = self.client.messages.create(
            model=self.model_name,  # e.g., "claude-3-7-sonnet-20250219",
            max_tokens=self.max_output_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=claude_messages,
        )
        self.total_duration_sec += time.perf_counter() - start_time

        #print(response.content)
        self.last_result = response.content[-1].text
        self.messages.append(Prompt(Prompt.ASSISTANT, self.last_result))

        self.total_iterations = len(self.messages)
        self.total_completion_chars += len(self.last_result)
        self.total_chars += len(self.last_result)
        # Record telemetry (Anthropic does not return usage yet in public API)
        self.total_prompt_tokens = None
        self.total_completion_tokens = None
        self.total_tokens = None

        logger.debug("Anthropic Claude returned: %s", self.last_result)
        return self.last_result


if __name__ == "__main__":
    main_config = AIAgentConfig("claude-3-5-haiku-latest")
    main_agent = AIAgentAnthropicClaude(main_config)

    main_agent.system("You are a helpful assistant")
    MAIN_PROMPT = "What is the answer to life, the universe and everything?"
    print(f"User Prompt:\n{MAIN_PROMPT}")
    result = main_agent.ask(MAIN_PROMPT)
    print(f"\nOutput:\n{result}")
