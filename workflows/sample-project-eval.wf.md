# Sample Project Evaluation

This workflow autmatically evaluates a sourcecode sample project.

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    PARAMS@{ shape: comment, label: "REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git"}

    PROMPT_SYSTEM[Prompt: System] --> CALL_CHECKTOOLS
    CALL_CHECKTOOLS[[check-toolchain.wf.md]] --> CHECK_RESULT_SUCCESS{RESULT == 'SUCCESS'}

    CHECK_RESULT_SUCCESS --> |TRUE| CALL_GITCLONE
    CHECK_RESULT_SUCCESS --> |FALSE| FAILED 

    CALL_GITCLONE[[git-clone-repo.wf.md]] --> CHECK_CLONE_SUCCESS{RESULT == 'SUCCESS'}

    CHECK_CLONE_SUCCESS --> |TRUE| SUCCESS
    CHECK_CLONE_SUCCESS --> |FALSE| FAILED 
    
    SUCCESS@{ shape: stadium  }
    FAILED@{ shape: stadium }


    %% Event-handler: ON_FAILED
    ON_FAILED@{ shape: stadium } --> PROMPT_FAILED_REPORT
    PROMPT_FAILED_REPORT[Prompt: User Failed-Report]
```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

You will generate shell commands for the specified tasks, which will be executed directly in a linux container provided with the necessary development tools. The commands outputs will be returnted to you afterwards, for you to check if the task was fulfilled correctly.

Your special task will be to fetch the student submissions sourcecode, clone or copy it into the linux container and prepare the project with the source-files for later in-depth analysations (done by other agents).

Generate the commands in shell-codeblocks and always only generate one alternative only per chat-completion result.

## User Failed-Report

Your previous commands failed, see the results:
{{RESULT}}

Write a short summary about the issue.
Any ideas how to fix the problem?
