#!/bin/python
"""
The AI-Agent implementation using the Platform OpenAI
"""
import logging
from openai import OpenAI
from app.agents.agent_config import AIAgentConfig
from app.agents.agent import AIAgent



# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# app/agents/AIAgentOpenAI.py
class AIAgentOpenAI(AIAgent):
    """Accesses the OpenAI API, will keep track of the context"""
    def __init__(self, config):
        super().__init__(config)
        logger.debug("Initializing AIAgentOpenAI")

        self.client = OpenAI(
            api_key=config.ai_api_key,
            organization= config.ai_organization_id
        )
        self.model_name = config.ai_model_name

    def system(self, prompt: str) -> str:
        """Starts with a new context (a reset), and provides the chat-systems general behavior"""
        self.messages = []
        return super().system(prompt)

    def ask(self, prompt: str) -> str:
        """Sends a prompt to ChatGPT, will track the result in messages"""
        logger.debug("OpenAI ask prompt received: %s", prompt)
        super().ask(prompt)
        messages = [msg.to_dict() for msg in self.messages]
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )
        self.last_result = ""
        for choice in chat_completion.choices:
            self.last_result += choice.message.content + "\n"
        logger.debug("OpenAI returned: %s", self.last_result)
        return self.last_result


if __name__ == "__main__":
    main_config = AIAgentConfig()
    main_config.load_from_environment()

    main_agent = AIAgentOpenAI(main_config)

    main_agent.system("You are a helpful assistant")
    result = main_agent.ask("What is the answer to life, the universe and everything?")
    print(f"{result}")
