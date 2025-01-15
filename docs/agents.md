# AI-Agents

Classes respresenting the AI-Agents which will work on the tasks using chat completion.
The decision which AI-Technology/-Platform in which configuration to select is taken flexible on the time of AI-agent instance creation done by the AIAgentFactory.

# AI-Agent Classes
```mermaid
classDiagram
    class AIAgentConfig {
        + ai_api_key
        + ai_organization_name
        + ai_model_name
        + load_from_environment()
        + load_from_jsonfile(String filename)
        + load_from_json(String json_data)
    }

    class AIAgent {
        - List~str~ messages
        - AIAgentConfig config

        + AIAgent( AIAgentConfig config )
        + system( str prompt )* str
        + ask( str prompt )* str
        + advice( str question, str answer)* 
    }
    AIAgent o-- AIAgentConfig

    class AIAgentOpenAI {
        + AIAgentOpenAI( AIAgentConfig config )
        + system( str prompt ) str
        + ask( str prompt ) str
        + advice( str question, str answer)
    }
    AIAgent <|-- AIAgentOpenAI

    class AIAgentFactory {
        + create_agent()$ AIAgent
    }
    AIAgentFactory ..> AIAgent
```

## Prompt Classes
```mermaid
classDiagram
    class Prompt {
        + str role
        + str content
        + check()
    }

    class PromptEncoder {
        default( Prompt o )
    }
    JSONEncoder ()-- PromptEncoder
    PromptEncoder o-- Prompt

    class PromptDecoder {
        + dict_to_object() Prompt
    }
    JSONDecoder ()-- PromptDecoder
    PromptDecoder o-- Prompt

    class PromptFactory {
        + load( str filepath ) list~Prompt~
        + load_from_jsonfile( str filepath ) list~Prompt~
        + load_from_mdfile( str filepath ) list~Prompt~
        + load_from_textfile( str filepath ) list~Prompt~
    }
    PromptFactory ..> Prompt
```