#!/bin/python
"""
The AI-Agent implementation using the CodeLLAMA model from Hugging Face Transformers.
"""
import logging
import time
import os
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer, TextGenerationPipeline
from transformers.utils import logging as hf_logging
from huggingface_hub import HfApi
import torch
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
hf_logging.set_verbosity_error()  # Silence model loading logs



class AIAgentTransformers(AIAgent):
    """
    Generic agent using Hugging Face Transformers 
    for causal LLMs with automatic chat formatting support
    """

    def __init__(self, config):
        super().__init__(config)
        logger.info("Creating AIAgentTransformers with %s", config)

        self.model_name = config.model_name or "codellama/CodeLlama-13b-hf"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info("Loading model '%s' on device: %s", self.model_name, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True  # needed for some community models
        )

        # chat_template support
        if not getattr(self.tokenizer, "chat_template", None):
            # Manually set chat_template if not defined
            logger.warning("Tokenizer has no chat_template; setting Code Llama-compatible template manually.")
            self.tokenizer.chat_template = """{% for message in messages %}
        {{ '<|system|>' if message['role'] == 'system' else '<|user|>' if message['role'] == 'user' else '<|assistant|>' }}
        {{ message['content'].strip() }}
        {% endfor %} <|assistant|>
        """
        self.supports_chat_template = hasattr(self.tokenizer, "apply_chat_template") and callable(self.tokenizer.apply_chat_template)

        if self.device == "cuda":
            self.pipeline = TextGenerationPipeline(
                model=self.model,
                tokenizer=self.tokenizer,
                device=0)
        else:
            self.pipeline = TextGenerationPipeline(model=self.model,tokenizer=self.tokenizer)


    def system(self, prompt: str) -> str:
        """Starts with a new context (a reset), and provides the chat-system's general behavior"""
        logger.debug("Init AIAgentTransformers with system prompt: %s", prompt)
        self.messages = []
        return super().system(prompt)

    def ask(self, prompt: str) -> str:
        """Sends a prompt to the Transformer model, will track the result in messages"""
        logger.debug("Ask AIAgentTransformers: %s", prompt)
        if len(prompt) > self.max_prompt_length:
            prompt = trunc_middle(prompt, self.max_prompt_length)
            logger.warning("Prompt is too long, so truncated in the middle:\n%s", prompt)
        super().ask(prompt)

        full_prompt = self._build_prompt()

        start_time = time.perf_counter()
        output = self.pipeline(
            full_prompt,
            max_new_tokens=self.max_output_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
        )
        self.total_duration_sec += time.perf_counter() - start_time

        # Extract only newly generated text
        self.last_result = output[0]["generated_text"][len(full_prompt):]
        self.messages.append(Prompt(Prompt.ASSISTANT, self.last_result))

        self.total_iterations = len(self.messages)
        self.total_completion_chars += len(self.last_result)
        self.total_chars += len(self.last_result)

        logger.debug("Transformers model returned: %s", self.last_result)
        return self.last_result

    def _build_prompt(self) -> str:
        """Builds a prompt compatible with either a chat template or plain formatting"""
        if self.supports_chat_template:
            chat = []
            for msg in self.messages:
                if msg.role == Prompt.SYSTEM:
                    chat.append({"role": "system", "content": msg.content})
                elif msg.role == Prompt.USER:
                    chat.append({"role": "user", "content": msg.content})
                elif msg.role == Prompt.ASSISTANT:
                    chat.append({"role": "assistant", "content": msg.content})
            # Add latest user prompt as the final message (for interactive prompt completion)
            chat.append({"role": "user", "content": self.messages[-1].content})
            rendered = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
            logger.debug("Chat template formatted prompt:\n%s", rendered)
            return rendered
        else:
            # Basic formatting fallback
            formatted = ""
            for msg in self.messages:
                if msg.role == Prompt.SYSTEM:
                    formatted += f"<|system|>\n{msg.content}\n"
                elif msg.role == Prompt.USER:
                    formatted += f"<|user|>\n{msg.content}\n"
                elif msg.role == Prompt.ASSISTANT:
                    formatted += f"<|assistant|>\n{msg.content}\n"
            formatted += "<|user|>\n" + self.messages[-1].content + "\n<|assistant|>\n"
            logger.debug("Plain prompt formatting fallback:\n%s", formatted)
            return formatted



    @staticmethod
    def is_model_supported(model_name: str, try_load: bool = False) -> bool:
        """
        Checks whether a given Hugging Face model name:
        - Exists on Hugging Face Hub
        - Is downloadable
        - Is a causal language model (AutoModelForCausalLM)
        Returns True if compatible, otherwise False.
        """
        try:
            # Step 1: Check if model exists on HF Hub
            api = HfApi()
            model_card = api.model_info(model_name)
            if model_card is None or not model_card.id:
                return False

            # Step 2: Try to load tokenizer and model for causal LM
            if try_load:
                AutoTokenizer.from_pretrained(model_name)
                AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True  # needed for some community models
                )

            return True
        except Exception:
            return False


if __name__ == "__main__":
    main_config = AIAgentConfig("codellama/CodeLlama-7b-hf")
    main_agent = AIAgentTransformers(main_config)

    main_agent.system("You are a helpful assistant for software engineering tasks.")
    MAIN_PROMPT = "Write a function in Python that parses JSON into a dictionary."
    print(f"User Prompt:\n{MAIN_PROMPT}")
    result = main_agent.ask(MAIN_PROMPT)
    print(f"\nOutput:\n{result}")
