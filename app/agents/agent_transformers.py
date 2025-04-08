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

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level='DEBUG', #os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
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

        self.model_name = config.model_name or "codellama/CodeLlama-7b-Instruct-hf"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info("Loading model '%s' on device: %s", self.model_name, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True  # needed for some community models
        )
        self.pipeline = TextGenerationPipeline(model=self.model,tokenizer=self.tokenizer)
        self.supports_chat_template = hasattr(self.tokenizer,
            "apply_chat_template") and callable(self.tokenizer.apply_chat_template)


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


        # Build the prompt
        if self.supports_chat_template:
            # Use chat template if available
            try:
                tokenized_chat = self.tokenizer.apply_chat_template(
                    self.messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
                full_prompt = self.tokenizer.decode(tokenized_chat[0])
                logger.debug("Full tokenized prompt: %s", full_prompt)
            except Exception as e:
                logger.warning("Error tokenizing chat: %s", e)
                # Fallback to basic formatting
                self.supports_chat_template = False

        if not self.supports_chat_template:
            full_prompt = self._build_prompt()

        start_time = time.perf_counter()
        sequences = self.pipeline(
            full_prompt,
            do_sample=True,
            top_k=10,
            temperature=self.temperature,
            top_p=self.top_p,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            max_length=self.max_output_tokens,
            #max_new_tokens=self.max_output_tokens,
            #pad_token_id=self.tokenizer.pad_token_id,
        )
        self.total_duration_sec += time.perf_counter() - start_time

        # Extract only newly generated text
        output = ""
        for seq in sequences:
            output += f"{seq['generated_text']}\n"
        print(f"Result: {output}")
        self.last_result = output[len(full_prompt):].strip()
        self.messages.append(Prompt(Prompt.ASSISTANT, self.last_result))

        self.total_iterations = len(self.messages)
        self.total_completion_chars += len(self.last_result)
        self.total_chars += len(self.last_result)

        logger.debug("Transformers model returned: %s", self.last_result)
        return self.last_result


    def _build_prompt(self) -> str:
        """Builds a prompt compatible with either a chat template or plain formatting"""
        # Basic formatting fallback
        formatted = ""
        for msg in self.messages:
            if msg.role == Prompt.SYSTEM:
                formatted += f"<s><<SYS>>\n{msg.content}\n<</SYS>>\n\n"
            elif msg.role == Prompt.USER:
                formatted += f"{msg.content}\n\n<</INPUT>>\n\n"
            elif msg.role == Prompt.ASSISTANT:
                formatted += f"{msg.content}\n\n<</OUTPUT>>\n\n"
        logger.debug("Formatted Prompt:\n%s", formatted)
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
    main_config = AIAgentConfig("codellama/CodeLlama-7b-Instruct-hf")
    main_agent = AIAgentTransformers(main_config)

    main_agent.system("You are a helpful assistant for software engineering tasks.")
    MAIN_PROMPT = "Write a function in Python that parses JSON into a dictionary."
    print(f"User Prompt:\n{MAIN_PROMPT}")
    result = main_agent.ask(MAIN_PROMPT)
    print(f"\nOutput:\n{result}")
