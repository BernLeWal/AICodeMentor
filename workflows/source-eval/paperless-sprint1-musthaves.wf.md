# Paperless Sprint1 MUST-HAVEs

Fetch the student submissions sourcecode, clone or copy it into the linux container and prepare the project with the source-files for later in-depth analysations (done by other agents).

Tasks to fulfil:
- REPO_URL given
- git clone ok
- it is a java project with maven build 
- it compiles without error (no unit-tests executed)

Score: 
- 30 points is all tasks are ok
- 0 points if one of the tasks fails

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    PARAMS@{ shape: comment, label: "REPO_URL"}

    PROMPT_SYSTEM[Prompt: System] --> PROMPT_CLONE

    PROMPT_CLONE[Prompt: User Clone] --> EXECUTE_GITCLONE
    EXECUTE_GITCLONE[Execute: ] --> PROMPT_GITRESULTS

    PROMPT_GITRESULTS[Prompt: User GitCmdResults] --> CHECK_GITRESULT_SUCCESS{RESULT == 'SUCCESS'}
    CHECK_GITRESULT_SUCCESS --> |TRUE| PROMPT_BUILD
    CHECK_GITRESULT_SUCCESS --> |FALSE| FAILED

    PROMPT_BUILD[Prompt: User Build] --> EXECUTE_BUILD
    EXECUTE_BUILD[Execute: ] --> PROMPT_BUILDRESULTS

    PROMPT_BUILDRESULTS[Prompt: User BuildResults] --> CHECK_BUILDRESULT_SUCCESS{RESULT == 'SUCCESS'}
    CHECK_BUILDRESULT_SUCCESS --> |TRUE| SUCCESS
    CHECK_BUILDRESULT_SUCCESS --> |FALSE| CHECK_BUILDRESULT_FAILED{RESULT == 'FAILED'} 
    CHECK_BUILDRESULT_FAILED --> |TRUE| FAILED
    CHECK_BUILDRESULT_FAILED --> |FALSE| PROMPT_BUILD_IMPROVE
    PROMPT_BUILD_IMPROVE[Prompt: User Build Improve] --> EXECUTE_BUILD
    
    SUCCESS@{ shape: stadium  }
    FAILED@{ shape: stadium }
```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

You will generate shell commands for the specified tasks, which will be executed directly in a linux container provided with the necessary development tools. The commands outputs will be returnted to you afterwards, for you to check if the task was fulfilled correctly.

Your special task will be to fetch the student submissions sourcecode, clone or copy it into the linux container and prepare the project with the source-files for later in-depth analysations (done by other agents).

Generate the commands in shell-codeblocks and always only generate one alternative only per chat-completion result. Put every command in a new line.

## User Clone

Fulfill the following tasks:
- Change the current working directory to the home directory.
- Check if the URL "{{REPO_URL}}" is valid
- Git clone the repository {{REPO_URL}}
- Afterwards check if the files are existing and in which sub-directory the pom.xml file(s) are stored.

## User GitCmdResults

Your generated commands have been executed and the output is now shown to you.

It the output shows, that the repository is cloned correctly and the exact paths to the local project files is available, then just answer with the word "SUCCESS" in the first line.
Otherwise, if the output shows that the git commands failed or there is no project found, then just answer with the word "FAILED" in the first line.

In the following lines of your answer summarize with only a few sentences the outcome of your activities and state the paths to the project.

The console output of your generated commands are:  
```shell
{{RESULT}}
```

## User Build

Now fulfill the following tasks:
- Change the current working directory to the directory where the pom.xml file is stored (in order to allow the Maven tool to find the pom.xml)
- Build the project with Maven using the 'package' goal without running the tests

## User BuildResults

Your generated commands have been executed and the output is now shown to you.

If the output shows, that the project is built correctly without errors, then just answer with the word "SUCCESS" in the first line.
If the output shows, that Maven could not build the project or there are compile errors, then just answer with the word "FAILED" in the first line.
If you can't decide if SUCCESS or FAILED explicitly, or if you need another trial, then answer with the word "CONTINUE" in the first line.

In the following lines of your answer summarize with only a few sentences the outcome of your activities and state the paths to the built artifact.
Explicitly print the path to the project and where to find the pom.xml file (the other agents need this information).
Finally state that the total score is 30 points (because it succeeded)

The console output of your generated commands is:  
```shell
{{RESULT}}
```

## User Build Improve

Your previous suggestions of commands failed to build the source project.
Try it again using a different approach.

