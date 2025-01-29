# Clone Repository

Fetch the student submissions sourcecode, clone or copy it into the linux container and prepare the project with the source-files for later in-depth analysations (done by other agents).

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    PARAMS@{ shape: comment, label: "REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git"}

    PROMPT_SYSTEM[Prompt: System] --> PROMPT_CLONE
    PROMPT_CLONE[Prompt: User Clone] --> EXECUTE_OUTPUT
    EXECUTE_OUTPUT[Execute: ] --> PROMPT_CMDRESULTS

    PROMPT_CMDRESULTS[Prompt: User CommandResults] --> CHECK_RESULT_SUCCESS{RESULT == 'SUCCESS'}
    CHECK_RESULT_SUCCESS --> |TRUE| SUCCESS
    CHECK_RESULT_SUCCESS --> |FALSE| CHECK_RESULT_FAILED{RESULT == 'FAILED'} 

    CHECK_RESULT_FAILED --> |TRUE| FAILED
    CHECK_RESULT_FAILED --> |FALSE| PROMPT_IMPROVE

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

## User Clone

Change the current working directory to the home directory.
Git clone the repository {{REPO_URL}} into the local home directory.
Afterwards check if the files are existing and in which sub-directory the pom.xml file(s) are stored.

## User CommandResults

Your generated commands have been executed and the output is now shown to you.
If the output shows, that the repository is cloned correctly and the exact paths to the pom.xml files are available, then just answer with the word "SUCCESS" in the first line.
If the output shows, that the git commands failed or there are no pom.xml files, then just answer with the word "FAILED" in the first line.
If you can't decide if SUCCESS or FAILED explicitly, or if you need another trial, then answer with the word "CONTINUE" in the first line.
In the following lines of your answer summarize with only a few sentences the outcome of your activities and state the paths to the pom.xml file(s).

The console output of your generated commands are:  
```shell
{{RESULT}}
```

## User Improve

Your previous suggestions of commands failed to clone the repository.
Try it again use a different approach.
