# Check Toolchain

This workflow checks if the toolchain - consisting of git, maven and java - is available and working.

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM

    PROMPT_SYSTEM[Prompt: System] --> PROMPT_TESTGIT
    PROMPT_TESTGIT[Prompt: User TestGit] --> EXECUTE_OUTPUT
    EXECUTE_OUTPUT[Execute: ] --> PROMPT_CMDRESULTS

    PROMPT_CMDRESULTS[Prompt: User CommandResults] --> CHECKRESULT_SUCCESS{Check_Result: SUCCESS}
    CHECKRESULT_SUCCESS --> |TRUE| PROMPT_SUCCESS_SUMMARY
    CHECKRESULT_SUCCESS --> |FALSE| CHECKRESULT_FAILED{Check_Result: FAILED} 

    CHECKRESULT_FAILED --> |TRUE| PROMPT_FAIL_SUMMARY
    CHECKRESULT_FAILED --> |FALSE| PROMPT_IMPROVE

    PROMPT_SUCCESS_SUMMARY[Prompt: User SuccessSummary] --> SUCCESS
    PROMPT_FAIL_SUMMARY[Prompt: User FailedSummary] --> FAILED

    PROMPT_IMPROVE[Prompt: User Improve] --> EXECUTE_OUTPUT
    
    SUCCESS@{ shape: stadium  }
    FAILED@{ shape: stadium }
```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

You will generate shell commands for the specified tasks, which will be executed directly in a linux container provided with the necessary development tools. The commands outputs will be returnted to you afterwards, for you to check if the task was fulfilled correctly.

Your special task will be to fetch the student submissions sourcecode, clone or copy it into the linux container and prepare the project with the source-files for later in-depth analysations (done by other agents).

Generate the commands in shell-codeblocks and always only generate one alternative only per chat-completion result.

## User TestGit

Check if in the shell the git commands are installed correctly and if the github-server (https://www.github.com) is reachable via network.

## User CommandResults

Your generated commands have been executed and the output is now shown to you.
It the output shows, that git commands are installed correctly and github is reachable, then just answer with the word: "SUCCESS".
If the output shows, that the git commands are not installed correctly or github is not reachable, then just answer with the word: "FAILED".
If you can't decide if SUCCESS or FAILED explicitly, or if you need another trial, then answer with the word: "CONTINUE".

The console output of your generated commands are:  
```shell
{{CURRENT_RESULT}}
```

## User SuccessSummary

Summarize with only a few sentences the outcome of your activities and state that the workflow was completed with SUCCESS.

## User FailedSummary

Summarize with only a few sentences the outcome of your activities and state that the workflow FAILED.
Give brief suggestions what to do to fix the problem.

## User Improve

Your previous suggestions of commands failed to find out if in the shell the git commands are installed correctly and if github is reachable.
Try it again use a different approach.
