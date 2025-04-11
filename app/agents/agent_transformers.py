#!/bin/python
"""
The AI-Agent implementation using the CodeLLAMA model from Hugging Face Transformers.
"""
import logging
import time
import os
import gc
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer, TextGenerationPipeline
from transformers.utils import logging as hf_logging
from huggingface_hub import HfApi
import torch
import psutil
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

    # Singleton instance of the model resources (shared across all agents)
    _model_name = None
    _model = None
    _tokenizer = None
    _pipeline = None
    _device = None
    _supports_chat_template = False


    def __init__(self, config):
        super().__init__(config)
        logger.info("Creating AIAgentTransformers with %s", config)

        self.model_name = self.load_model(config.model_name)

        self.messages = []


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
        if AIAgentTransformers._supports_chat_template:
            # Use chat template if available
            try:
                tokenized_chat = AIAgentTransformers._tokenizer.apply_chat_template(
                    self.messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
                full_prompt = AIAgentTransformers._tokenizer.decode(tokenized_chat[0])
                logger.debug("Full tokenized prompt: %s", full_prompt)
            except Exception as e:
                logger.warning("Error tokenizing chat: %s", e)
                # Fallback to basic formatting
                AIAgentTransformers._supports_chat_template = False

        if not AIAgentTransformers._supports_chat_template:
            full_prompt = self._build_prompt()

        start_time = time.perf_counter()
        sequences = AIAgentTransformers._pipeline(
            full_prompt,
            do_sample=True,
            top_k=10,
            temperature=self.temperature,
            top_p=self.top_p,
            num_return_sequences=1,
            eos_token_id=AIAgentTransformers._tokenizer.eos_token_id,
            #max_length=self.max_output_tokens, # --> may lead to truncation
            max_new_tokens=self.max_output_tokens,
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
        logger.debug("Execution stats: duration_sec=%d, iterations=%d, completion_chars=%d, total_chars=%d",
                    self.total_duration_sec, self.total_iterations,
                    self.total_completion_chars, self.total_chars)
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
                return True if AIAgentTransformers.load_model(model_name) is not None else False

            return True
        except Exception:
            return False


    @staticmethod
    def load_model(model_name: str = None)->str:
        if model_name is None:
            model_name = "microsoft/Phi-4-mini-instruct"
        if AIAgentTransformers._model_name == model_name:
            logger.debug("Model already loaded: %s", model_name)
            return AIAgentTransformers._model_name
        if AIAgentTransformers._model is not None:
            logger.info("Unload previously loaded model %s and releasing resources.",
                        AIAgentTransformers._model_name)
            AIAgentTransformers.unload_model()

        AIAgentTransformers._model_name = model_name
        AIAgentTransformers._device = "cuda" if torch.cuda.is_available() else "cpu"

        AIAgentTransformers.log_memory_usage("Before loading")
        logger.info("Loading model '%s' on device: %s",
                    AIAgentTransformers._model_name,
                    AIAgentTransformers._device)
        AIAgentTransformers._tokenizer = AutoTokenizer.from_pretrained(model_name)
        AIAgentTransformers._model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True  # needed for some community models
        )
        AIAgentTransformers._pipeline = TextGenerationPipeline(
            model=AIAgentTransformers._model,
            tokenizer=AIAgentTransformers._tokenizer)
        AIAgentTransformers._supports_chat_template = hasattr(AIAgentTransformers._tokenizer,
            "apply_chat_template") and callable(AIAgentTransformers._tokenizer.apply_chat_template)
        AIAgentTransformers.log_memory_usage("After loading")


    @staticmethod
    def unload_model():
        """Release model, tokenizer and free up GPU/CPU memory"""
        logger.debug("Cleaning up AIAgentTransformers resources")
        AIAgentTransformers.log_memory_usage("Before cleanup")

        # Explicitly delete objects
        if AIAgentTransformers._model is not None:
            del AIAgentTransformers._model
        if AIAgentTransformers._tokenizer is not None:
            del AIAgentTransformers._tokenizer
        if AIAgentTransformers._pipeline is not None:
            del AIAgentTransformers._pipeline

        # If on CUDA: empty cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()  # optional: release inter-process cached memory

        gc.collect()  

        AIAgentTransformers.log_memory_usage("After cleanup")
        logger.debug("Cleanup completed for AIAgentTransformers")


    @staticmethod
    def log_memory_usage(label: str):
        """Logs memory usage of GPU and CPU"""
        process = psutil.Process(os.getpid())
        cpu_mem = process.memory_info().rss / (1024 * 1024)  # in MB
        if torch.cuda.is_available():
            gpu_mem = torch.cuda.memory_allocated() / (1024 * 1024)  # in MB
            logger.info("%s - CPU Memory Usage: %.2f MB | GPU Memory Usage: %.2f MB", label, cpu_mem, gpu_mem)
        else:
            logger.info("%s - CPU Memory Usage: %.2f MB", label, cpu_mem)


if __name__ == "__main__":
    main_config = AIAgentConfig("deepseek-ai/deepseek-coder-7b-instruct-v1.5")

    main_agent1 = AIAgentTransformers(main_config)
    main_agent2 = AIAgentTransformers(main_config) # Will share the same model

    system_prompt = "You are a helpful assistant for software engineering tasks."

    try:
        main_agent1.system(system_prompt)
        prompt1 = "Explain polymorphism in OOP with a Python sample."
        print(f"User Prompt 1:\n{prompt1}")
        result = main_agent1.ask(prompt1)
        print(f"\nOutput:\n{result}")

        print("\n-----------------------------------------------------\n")

        main_agent2.system(system_prompt)
        prompt2 = "Explain what is a decorator with a Python sample."
        print(f"User Prompt 2:\n{prompt2}")
        result = main_agent2.ask(prompt2)
        print(f"\nOutput:\n{result}")
    finally:
        main_agent1.cleanup()
        main_agent2.cleanup()

    del main_agent1 # will also call .cleanup()
    del main_agent2

    AIAgentTransformers.unload_model()
