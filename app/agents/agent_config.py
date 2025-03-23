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
class AIAgentConfig:
    """Retrieves the configuration for the AI Agents"""
    def __init__(self):
        self.ai_api_key = None
        self.ai_organization_id = None

    def load_from_environment(self):
        """loads the configuration from the environment variables"""
        logger.debug("Loading configuration from environment...")
        self.ai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.ai_organization_id = os.getenv('OPENAI_ORGANIZATION_ID', '')
        logger.debug(self)

    def load_from_jsonfile(self, filename):
        """loads the configuration from a JSON file"""
        # Load the configuration from the JSON file
        logger.debug("Loading configuration from file: %s", filename)
        with open(filename, 'r', encoding='utf-8') as file:
            config = json.load(file)
            self.ai_api_key = config['OPENAI_API_KEY']
            self.ai_organization_id = config['OPENAI_ORGANIZATION_ID']
        logger.debug(self)

    def load_from_json(self, json_data : str):
        """loads the configuration from a JSON string"""
        # Load the configuration from the JSON string
        logger.debug("Loading configuration from JSON string")
        config = json.loads(json_data)
        self.ai_api_key = config['OPENAI_API_KEY']
        self.ai_organization_id = config['OPENAI_ORGANIZATION_ID']
        logger.debug(self)

    # convert to str
    def __str__(self):
        return "AIAgentConfig: " + \
            f"OPENAI_API_KEY={self.ai_api_key[:4]}...{self.ai_api_key[-4:]}, " + \
            f"OPENAI_ORGANIZATION_ID={self.ai_organization_id[:4]}"+\
            f"...{self.ai_organization_id[-4:]}"


if __name__ == "__main__":
    main_config = AIAgentConfig()
    main_config.load_from_environment()
    print(main_config)
