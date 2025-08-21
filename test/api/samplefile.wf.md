# Lesson 1 - 42

AI CodeMentor Tutorial: Write your own Workflow - [Lesson 1](../../docs/tutorial/lesson1.md)

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    PROMPT_SYSTEM[Prompt: System] --> PROMPT_ASK
    PROMPT_ASK[Prompt: User Ask] --> SUCCESS
    SUCCESS@{ shape: stadium  }
```

# Prompts

## System

You are a helpful assistant.

## User Ask

What is the answer to life, the universe and everything?

