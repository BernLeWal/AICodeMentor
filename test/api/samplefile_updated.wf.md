# Lesson 2 - Who Am I

AI CodeMentor Tutorial: Write your own Workflow - [Lesson 2](../../docs/tutorial/lesson2.md)

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    PROMPT_SYSTEM[Prompt: System] --> PROMPT_WHOAMI
    PROMPT_WHOAMI[Prompt: User WhoAmI] --> EXECUTE_OUTPUT
    EXECUTE_OUTPUT[Execute: ] --> SUCCESS
    SUCCESS@{ shape: stadium  }
```

# Prompts

## System

You are a helpful assistant.

You will generate shell commands for the specified tasks, which will be executed directly in a linux container provided with the necessary command-line tools.

Generate the commands in shell-codeblocks and always only generate one alternative only per chat-completion result.

## User WhoAmI

Show the name of the current user.
Afterwards check which linux and bash versions are running.
Finally also show me the installed python version.

