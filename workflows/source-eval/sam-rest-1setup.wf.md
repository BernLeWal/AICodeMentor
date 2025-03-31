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
    PROMPT_SYSTEM[Prompt: System] --> ASSIGN_FINDPROJECT

    ASSIGN_FINDPROJECT[Assign: User FindProjectFiles] --> CALL_COTH_FINDPROJECT
    CALL_COTH_FINDPROJECT[[../coth.wf.md]] --> ASSIGN_BUILD

    ASSIGN_BUILD[Assign: User BuildProject] --> CALL_COTH_BUILDPROJECT
    CALL_COTH_BUILDPROJECT[[../coth.wf.md]] --> PROMPT_SUMMARY

    PROMPT_SUMMARY[Prompt: User Summary] --> SUCCESS
    SUCCESS@{ shape: stadium  }
```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

Your special task will be to check by using bash commands, if the Java Spring Boot project files are existing in the {{PROJECT_DIR}} and use the Maven tool to build the application. For every tasks you give score points based on the results.
Finally you will write a short text to summarize the results.

Don't add suggestions for improvements.
Don't add content which was not stated before explicitly.

## User FindProjectFiles

Fulfill the following tasks: 
- Check if the directory {{PROJECT_DIR}} contains a Java Spring Boot project with a Maven build system.
- Check in which sub-directory of the project directory:{{PROJECT_DIR}} the pom.xml file is stored and return the full path
- Change the current working directory to the directory where the pom.xml file is stored

## User BuildProject

Fulfill the following tasks:
Run Maven with the 'package' goal. 
Summarize the build and test results. 

## User Summary

Summarize the outcome of your activities.
Score the provided java project depending on the results you found within your activities with 20 points maximum (if everything was fulfilled)
