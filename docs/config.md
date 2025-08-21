# AI-Agent Configuration

## Configuration Parameters

The following parameters can be set in the [.env](../.env) file.

* **AI_MODEL_NAME**:  
    The LLM model name used by the `AIAgent` and derived.
    The `AIAgentFactory` will take this setting to automatically create the corresponding implementation class derived from the `AIAgent` base class.

    Commonly used models are:
    - **Platform OpenAI GPT Chat** Models: starting with "gpt-", e.g. `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`, `gpt-4-turbo`, `gpt-4`,..
    - **Platform OpenAI Reasoning** Models: starting with "o1-", "o3-", e.g. `o1-mini`, (`o1`), `o3-mini`, (`o3-mini-high`)

* **AI_TEMPERATURE**:  
    Controls the randomness of the output.  

    - Value Range: `0.0` - `2.0`; Default Value: `1.0`
    - Lower values (e.g., 0.0–0.3) make the model more deterministic and focused; it will produce the most likely completions.  
    Use temperature = 0.0 for factual QA or technical explanations.
    - Higher values (e.g., 0.8–1.2) increase creativity and variability in responses.  
    Use temperature ≈ 1.0 for brainstorming, storytelling, or creative writing.

* **AI_TOP_P** ("nucleus sampling"):  
    Limits token sampling to a cumulative probability mass.

    - Value Range: `0.0`- `1.0`; Default Value: `1.0`
    - Example: If top_p = 0.9, the model considers only the top 90% most likely next tokens. Reduces randomness while still allowing for creativity.
    - Recommendation: use either temperature or top_p. Use top_p as an alternative to temperature if you want to cap randomness more explicitly.

* **AI_FREQUENCY_PENALTY**:  
    Penalizes tokens that have already appeared in the response.
    Helps avoid looping or redundant outputs.

    - Value Range: `0.0`- `2.0`; Default Value: `0.0`
    - Higher values discourage repetition.

* **AI_PRESENCE_PENALTY**:  
    Encourages the model to introduce new topics or vocabulary.
    Useful when diverse ideas or brainstorming are required.

    - Value Range: `0.0`- `2.0`; Default Value: `0.0`
    - Higher values promote novelty in the generated output.

    Remarks: presence_penalty considers whether a word has appeared at all, while frequency_penalty considers how often it has appeared.

* **AI_MAX_OUTPUT_TOKENS**:  
    Specifies the maximum number of tokens in the output.
    Use to limit verbosity or response cost.

    - Value of type int; Default: `None`
    - Set to a specific value (e.g., 512) if you need fixed-length outputs for downstream processing.

* **AI_STOP_SEQUENCE**:  
    Specifies one or more strings at which the model will stop generating further tokens.
    Useful in multi-turn conversations or function calling setups.
    For example, using ["User:", "Assistant:"] to terminate once a role marker is reached.
