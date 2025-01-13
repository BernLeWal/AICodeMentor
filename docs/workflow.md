# Workflow

- A **Workflow** is started by an objective given from the user, e.g. grade a student submission
- The **Workflow** consists of multiple activities which will be run like a flow-diagram (divide and concquer)
- Possible tasks are: start, create agent (returns an agent), prompt agent (returns the agent's output), execute commands, checkpoint, finish
- A **Workflow** may use sub-**Workflow**s
- Within a workflow AI-agents use the tool-chain (**CommandExecutors**), colloberate to each other, and with the user (if required)
- The **WorkflowInterpreter** provides the shared context between all AI-agents, the tool-chain, and the user for collaboration
- The **WorkflowInterpreter** controls the execution of the collaboration, executes the parties (AI-Agents, Commands), checks the overall status of tasks and the workflow, and interrupts/fails the workflow on problems
- The **WorkflowInterpreter** will limit the collaboration due to, cost limits of AI-APIs, char/token limits, time limits, and iteration limits

## Class Diagrams

```mermaid
classDiagram
    class Workflow {
        - str id
        - str name
        - list~Activity~ activities
        - Activity start

        - int status # DOING, SUCCESS, FAILED
        - str result
        - Workflow parent
        - WorkflowInterpeter interpreter
    }
    Workflow "1" *-- "n" Workflow

    class WorkflowInterpreter {
        - Workflow workflow
        - Agent agent
        + start(params)
        + prompt(str prompt_id)
        + execute()
        + check_status(int expected_status) bool
        + check_result(str expected_text, int operation) bool
        + success()
        + failed()
    }
    WorkflowInterpreter *-- Workflow

    class Activity {
        - int kind # START, PROMPT, EXECUTE, CHECK_STATUS, CHECK_RESULT, SUCCESS, FAILED
        - str name
        - str expression
        - Activity next
        - Activity other
        - int hits
    }
    Workflow "1" *-- "n" Activity
```

## Workflow Charts

### Workflow 1: "Check toolchain"
This (sub-) workflow is used for (unit)-testing.

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    START_COMMENT@{ shape: comment, label: "no input parameters"}

    PROMPT_SYSTEM[Prompt: System] --> PROMPT_TESTGIT
    PROMPT_TESTGIT[Prompt: User TestGit] --> EXECUTE_OUTPUT
    EXECUTE_OUTPUT[Execute: ShellCommands] --> PROMPT_CMDRESULTS

    PROMPT_CMDRESULTS[Prompt: User CommandResults] --> CHECK_RESULT_SUCCESS{Check: Result==SUCCESS?}
    CHECK_RESULT_SUCCESS --> |TRUE| PROMPT_SUCCESS_SUMMARY
    CHECK_RESULT_SUCCESS --> |FALSE| CHECK_RESULT_FAILED{Check: Result==FAILED?} 

    CHECK_RESULT_FAILED --> |TRUE| PROMPT_FAIL_SUMMARY
    CHECK_RESULT_FAILED --> |FALSE| PROMPT_IMPROVE

    PROMPT_SUCCESS_SUMMARY[Prompt: User SuccessSummary] --> SUCCESS
    PROMPT_FAIL_SUMMARY[Prompt: User FailedSummary] --> FAILED

    PROMPT_IMPROVE[Prompt: Improve] --> EXECUTE_OUTPUT
    
    SUCCESS@{ shape: stadium  }
    FAILED@{ shape: stadium }

    style PROMPT_SYSTEM stroke:#000,stroke-width:4px,fill:#80a0ff
```