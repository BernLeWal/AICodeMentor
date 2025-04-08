# Setup LLM Integrations

AICodeMentor integrates various LLMs from different vendors.

Find here the documentation how to setup the solution of your choice (you will need one of those minimum).

## OpenAI: Platform OpenAI API

### Setup 
To use the LLMs from OpenAI you need to
- You need an **[Platform OpenAI](https://platform.openai.com/)** account
- it is necessary to provide billing information, and add the first payment to create a budget, e.g. 10$
- create an API-Key and configure it in the [.env](../.env) file. (A template for that file is [.env.sample](../.env.sample) )

To make it work in Python the following packages have to be installed, this is
(already) fulfilled when using [requirements.txt](../requirements.txt): 
```pip install openai```

### Models
The OpenAI integration is used on all model-names starting with:
- "gpt-": (using class AIAgentOpenAIGpt), e.g.:
  - "gpt-4o-mini",
  - "gpt-4o" (Attention: expensive),
  - "gpt-4-turbo",
  - "gpt-4"  (Attention: expensive),
  - "gpt-3.5-turbo",
- "o1", "o3": (using class AIAgentOpenGptInstruct), e.g.:
  - "o3-mini",
  - "o1-mini",
  - "o1" (Attention: expensive),

### Links
- For a list of OpenAI models see: https://platform.openai.com/docs/models
- To manage your costs, see: https://platform.openai.com/settings/organization/usage

## Google Cloud: Generative Language API (Gemini)

### Setup
To use the LLMs from Google Cloud you need to
1. (a pre-requisite) Register your Google Account as Google Developer Account in https://console.cloud.google.com
2. (pre-requisite) Create a new Google Cloud Project: https://console.cloud.google.com/projectcreate
3. Enable the API: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com
    - Optional: Create Credentials: Service Account
    - Create Credentials: OAuth 2.0 Client IDs  
      --> then download the JSON file into the [secrets/](../secrets/) directory and set the path in the [.env](../.env) file. (A template for that file is [.env.sample](../.env.sample) )

To make it work in Python the following packages have to be installed, this is
(already) fulfilled when using [requirements.txt](../requirements.txt): 
```pip install google-auth google-generativeai```

### Models
The Google Gemini Integration is used on all model-names starting with:
- "gemini-": (using class AIAgentGoogleGemini), e.g.:
  - "gemini-2.0-flash" (Attention: expensive),
  - "gemini-2.0-flash-lite",
  - "gemini-1.5-flash",
  - "gemini-2.0-flash-thinking-experimental" (Attention: expensive),

### Links
- For a list of OpenAI models see: https://ai.google.dev/gemini-api/docs/models
- To manage your costs, use Google Cloud Dashboard: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/cost

## Anthropic: Claude API

### Setup
To use the LLMs from Anthropic you need to
1. Create a user at https://console.anthropic.com
2. it is necessary to provide billing information, and add the first payment to create a budget, e.g. 10$
3. Create a new API-Key in https://console.anthropic.com/settings/keys and configure it in the [.env](../.env) file. (A template for that file is [.env.sample](../.env.sample) )

To make it work in Python the following packages have to be installed, this is 
(already) fulfilled when using [requirements.txt](../requirements.txt):
```pip install anthropic```

### Models
The Anthropic Claude Integration is used on all model-names starting with:
- "claude-": (using class AIAgentAnthropicClaude), e.g.:
  - "claude-3-7-sonnet-latest" (Attention: expensive),
  - "claude-3-5-haiku-latest",
  - "claude-3-opus-latest",
  - "claude-3-5-sonnet-latest" (Attention: expensive),
  - "claude-3-haiku-20240307",

### Links
- For a list of Anthropic models see: https://docs.anthropic.com/en/docs/about-claude/models/all-models
- To manage your costs, see: https://console.anthropic.com/settings/cost

## HuggingFace Transformers

### Setup
The models from HuggingFace are executed on the local machine. Ensure that you have a GPU available (with CPU-only execution lasts too long)
* see Setup Guide [setup_cuda.md](setup_cuda.md)

To make it work in Phython the following packages have to be installed, this is
(already) fulfilled when using [requirements.txt](../requirements.txt):
```pip install transformers accelerate ```

### Models
a complete list see: https://huggingface.co/models?language=code
The AIAgentFactory will detect via HuggingFace-API if the model name is existing before the AIAgentTransformers is created.

The following models have been tried successfully:
- "codellama/CodeLlama-7b-Instruct-hf" (7B; see https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf)
- "codellama/CodeLlama-13b-Instruct-hf" (13B; see https://huggingface.co/codellama/CodeLlama-13b-Instruct-hf)
- "codellama/CodeLlama-7b-hf" (7B; see https://huggingface.co/codellama/CodeLlama-7b-hf)
- "codellama/CodeLlama-13b-hf" (13B; see https://huggingface.co/codellama/CodeLlama-13b-hf)
- "Qwen/Qwen2.5-Coder-7B-Instruct" (7B, 128kT context; see https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
- "Qwen/Qwen2.5-Coder-14B-Instruct" (13B, 128kT context; see https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct
- "microsoft/Phi-4-mini-instruct" (4B, 128kT context; see https://huggingface.co/microsoft/Phi-4-mini-instruct)

The following models have been tested, but don't match to the used chat template - don't use them so far:
- "bigcode/starcoder2-7b" (7B; see https://huggingface.co/bigcode/starcoder2-7b)
- "bigcode/starcoder2-3b" (3B; see https://huggingface.co/bigcode/starcoder2-3b)


### Links
- Huggingface official website: https://huggingface.co/

- https://medium.com/aimonks/code-llama-quick-start-guide-and-prompt-engineering-eb1de8758399
- https://huggingface.co/docs/transformers/chat_templating
- https://huggingface.co/codellama/CodeLlama-13b-hf?ref=maginative.com
- https://docs.vultr.com/how-to-use-code-llama-large-language-model-on-vultr-cloud-gpu

---

## Model Comparison

### Context Window

The Context Window is the amount of previous tokens
which are considered for the current answer.
The model will "forget" the content and answers which
are outside the context window.

| Model       | Context Window (Tokens) | A4 pages (approx.) | 
|-------------|---------|------------|
| gpt-3       |    2048 | ~  3 pages | 
| gpt-3.5     |    4096 | ~  6 pages |
| gpt-4       |    8192 | ~ 12 pages |
| gpt-4o      |  128000 | ~183 pages |
| claude-2    |  100000 | ~143 pages |
| claude-3    |  200000 | ~286 pages |
| gemini      |   32768 | ~ 47 pages |
| gemini-1.5  | 1000000 |~1429 pages |
