#!/bin/python
"""
Retrieves the configuration for the AI Agents
"""
import os
import logging
import json
from dotenv import load_dotenv


load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


# app/agents/AIAgentConfig.py
# FIXME: this class does not fit anymore, with AI-Agents from different vendors
class AIAgentConfig:
    """Retrieves the configuration for the AI Agents"""
    def __init__(self, model_name:str = None):
        # Generic configuration
        if model_name is None:
            self.model_name = AIAgentConfig.get_model_name()
        else:
            self.model_name = model_name
        # Vendor specific configuration
        self.openai_api_key = None
        self.openai_organization_id = None
        self.google_client_secret_file = None
        self.anthropic_api_key = None

    def load_from_environment(self):
        """loads the configuration from the environment variables"""
        logger.debug("Loading configuration from environment...")
        # OpenAI:
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_organization_id = os.getenv('OPENAI_ORGANIZATION_ID', '')
        # Google Cloud:
        self.google_client_secret_file = os.getenv('GOOGLE_CLIENT_SECRET_FILE', '')
        # Anthropic:
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')

        logger.debug(self)

    def load_from_jsonfile(self, filename):
        """loads the configuration from a JSON file"""
        # Load the configuration from the JSON file
        logger.debug("Loading configuration from file: %s", filename)
        with open(filename, 'r', encoding='utf-8') as file:
            config = json.load(file)
            self.__dict__ = json.loads(config)
        logger.debug(self)

    def load_from_json(self, json_data : str):
        """loads the configuration from a JSON string"""
        # Load the configuration from the JSON string
        logger.debug("Loading configuration from JSON string")
        config = json.loads(json_data)
        self.__dict__ = json.loads(config)
        logger.debug(self)

    # convert to str
    def __str__(self):
        return "AIAgentConfig: " + \
            f"OPENAI_API_KEY={self.openai_api_key[:4]}...{self.openai_api_key[-4:]}, " + \
            f"OPENAI_ORGANIZATION_ID={self.openai_organization_id[:4]}"+\
            f"...{self.openai_organization_id[-4:]}"


    # ------------------------------------------------------
    @staticmethod
    def get_model_name() -> str:
        """
        Returns the model name of the AI-Agent instance
        """
        return os.getenv('AI_MODEL_NAME', 'gpt-4o-mini')

    @staticmethod
    def get_temperature() -> float:
        """
        Returns the temperature of the AI-Agent instance
        """
        return float(os.getenv('AI_TEMPERATURE', '0.7'))

    @staticmethod
    def get_top_p() -> float:
        """
        Returns the top-p value of the AI-Agent instance
        """
        return float(os.getenv('AI_TOP_P', '1.0'))

    @staticmethod
    def get_frequency_penalty() -> float:
        """"
        Returns the frequency penalty of the AI-Agent instance
        """
        return float(os.getenv('AI_FREQUENCY_PENALTY', '0.0'))

    @staticmethod
    def get_presence_penalty() -> float:
        """
        Returns the presence penalty of the AI-Agent instance
        """
        return float(os.getenv('AI_PRESENCE_PENALTY', '0.0'))

    @staticmethod
    def get_max_output_tokens() -> int:
        """
        Returns the maximum number of output tokens of the AI-Agent instance
        """
        return int(os.getenv("AI_MAX_OUTPUT_TOKENS", '1024'))

    @staticmethod
    def get_stop_sequences() -> list:
        """
        Returns the stop sequences of the AI-Agent instance
        """
        stop_seq:str = os.getenv('AI_STOP_SEQUENCE', None)     # stop gen. at this seq.
        return stop_seq.split('|') if stop_seq else None


if __name__ == "__main__":
    main_config = AIAgentConfig()
    main_config.load_from_environment()
    print(main_config)
