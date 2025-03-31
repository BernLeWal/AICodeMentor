# SAM Practice 1 REST - 1. Project Setup

Tasks to fulfil
- PROJECT_DIR given
- check that there is a java project with maven build
- it compiles without error

Score: up to 20 points maximum

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    PARAMS@{ shape: comment, label: "PROJECT_DIR"}
    PROMPT_SYSTEM[Prompt: System] --> ASSIGN_ADDONS

    ASSIGN_ADDONS[Assign: User FindAddons] --> CALL_COTH_ADDONS
    CALL_COTH_ADDONS[[../coth.wf.md]] --> PROMPT_SUMMARY

    PROMPT_SUMMARY[Prompt: User Summary] --> SUCCESS
    SUCCESS@{ shape: stadium  }
```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

Your special task will be to generate bash commands to check the files in {{PROJECT_DIR}} and below for additional information and documentation. For every tasks you give score points based on the results.
Finally you will write a short text to summarize the results.

Don't add suggestions for improvements.
Don't add content which was not stated before explicitly.

## User FindAddons

Fulfill the following tasks:
- Check if the user has additional Unit tests implemented.
- Check if there is any student created documentation available
- Check if any configuration data for REST clients is existing
in the {{PROJECT_DIR}} and below.

## User Summary

Summarize the outcome of your activities.
Score the provided java project depending on the results you found within your activities with 10 points maximum (if everything was fulfilled)
