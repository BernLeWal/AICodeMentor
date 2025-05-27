#!/bin/python
"""
The AI-Agent implementation using the Platform OpenAI GPT models (gpt-)
"""
import logging
import os
import time
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.generativeai as genai
from google.auth.transport.requests import Request
from app.util.string_utils import trunc_middle
from app.agents.agent_config import AIAgentConfig
from app.agents.agent import AIAgent
from app.agents.prompt import Prompt


load_dotenv()
log_level = os.getenv('LOGLEVEL', 'INFO').upper()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=log_level,
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)
# set the logger for the Google Gemini SDK
logging.getLogger("google.generativeai").setLevel(log_level)


# Scopes required to access the Gemini API (adjust as needed)
GEMINI_SCOPES = ["https://www.googleapis.com/auth/generative-language.tuning"]


class AIAgentGoogleGemini(AIAgent):
    """Accesses Google's Gemini API using OAuth2 credentials, maintains conversation context."""

    def __init__(self, config):
        super().__init__(config)
        logger.info("Creating AIAgentGoogleGemini with OAuth2 config: %s", config)

        # Load OAuth2 credentials
        self.credentials = self.load_credentials(config.google_client_secret_file)

        genai.configure(credentials=self.credentials)
        self.model = genai.GenerativeModel(self.model_name)
        self.chat_session = self.model.start_chat(history=[])


    def load_credentials(self, client_secret_path: str):
        """Loads OAuth 2.0 credentials from the client_secret.json file."""
        #client_secret_path = os.path.abspath(client_secret_path)
        logger.debug("Loading Google OAuth2 credentials from: %s", client_secret_path)
        token_path = client_secret_path.replace(".json", "_token.json")

        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, GEMINI_SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_path, GEMINI_SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())

        logger.info("Google OAuth2 credentials loaded successfully.")
        logger.debug("Stored OAuth2 token in: %s", token_path)
        return creds


    def system(self, prompt: str) -> str:
        """Starts a new chat with a simulated system message."""
        logger.debug("Init AIAgentGoogleGemini with system prompt: %s", prompt)
        self.messages = []
        self.chat_session = self.model.start_chat(history=[])
        self.chat_session.send_message(prompt)
        return super().system(prompt)


    def ask(self, prompt: str) -> str:
        """Sends a prompt to Gemini and processes the assistant's response."""
        logger.debug("Ask AIAgentGoogleGemini: %s", prompt)
        if len(prompt) > self.max_prompt_length:
            prompt = trunc_middle(prompt, self.max_prompt_length)
            logger.warning("Prompt is longer than %d (AI_MAX_PROMPT_LENGTH), so truncated in the middle:\n%s",
                           self.max_prompt_length, prompt)


        super().ask(prompt)

        start_time = time.perf_counter()
        response = self.chat_session.send_message(
            prompt,
            generation_config={
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": 1, # TODO - add top_k to config
                "max_output_tokens": self.max_output_tokens,
                "stop_sequences": self.stop_sequences,
            }
        )
        self.total_duration_sec += time.perf_counter() - start_time

        self.last_result = response.text
        self.messages.append(Prompt(Prompt.ASSISTANT, self.last_result))

        self.total_iterations = len(self.messages)
        self.total_completion_chars += len(self.last_result)
        self.total_chars += len(self.last_result)
        # Token usage is not reported in Gemini API (as of now)
        self.total_prompt_tokens = None
        self.total_completion_tokens = None
        self.total_tokens = None

        logger.debug("Gemini returned: %s", self.last_result)
        return self.last_result


if __name__ == "__main__":
    main_config = AIAgentConfig("gemini-2.0-flash-lite")
    main_agent = AIAgentGoogleGemini(main_config)

    main_agent.system("You are a helpful assistant")
    MAIN_PROMPT = "What is the answer to life, the universe and everything?"
    print(f"User Prompt:\n{MAIN_PROMPT}")
    result = main_agent.ask(MAIN_PROMPT)
    print(f"\nOutput:\n{result}")
