# Paperless Sprint1 Run Tests

Tasks to do:

- unit tests are existing and running without failures
- REST-Server starts successfully
- REST-Endpoints can be executed successfully
    - GET /api/documents: returns HTTP 2xx
    - POST /api/documents/post_document: returns HTTP 2xx
- REST-Server stops successfully

Maximum total Score: 30 points 

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM

    PROMPT_SYSTEM[Prompt: System] --> PROMPT_CD

    PROMPT_CD[Prompt: User Change Directory] --> EXECUTE_DIR
    EXECUTE_DIR[Execute: ] --> PROMPT_UNITTESTS

    PROMPT_UNITTESTS[Prompt: User Run UnitTests] --> EXECUTE_TESTS
    EXECUTE_TESTS[Execute: ] --> PROMPT_TESTRESULTS
    PROMPT_TESTRESULTS[Prompt: User UnitTest Results] --> EXECUTE_START

    EXECUTE_START[Execute: mvn spring-boot:start > /dev/null] --> PROMPT_REST

    PROMPT_REST[Prompt: User Test REST Endpoints] --> EXECUTE_REST
    EXECUTE_REST[Execute: ] --> PROMPT_RESTRESULTS

    PROMPT_RESTRESULTS[Prompt: User REST Test Results] --> CHECK_RESTRESULTS_SUCCESS{RESULT == 'SUCCESS'}
    CHECK_RESTRESULTS_SUCCESS --> |TRUE| EXECUTE_STOP
    CHECK_RESTRESULTS_SUCCESS --> |FALSE| PROMPT_REST_IMPROVE
    PROMPT_REST_IMPROVE[Prompt: User Improve Test REST Endpoints] --> EXECUTE_REST

    EXECUTE_STOP[Execute: mvn spring-boot:stop > /dev/null] --> PROMPT_SUMMARY

    PROMPT_SUMMARY[Prompt: User Summary] --> SUCCESS

    SUCCESS@{ shape: stadium  }

```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

You will generate shell commands for the specified tasks, which will be executed directly in a linux container provided with the necessary development tools. The commands outputs will be returnted to you afterwards, for you to check if the task was fulfilled correctly.

Your special task will be use the Maven tool to run the tests of the provided java software project, start the application, perform REST tests, and stop the application. For every tasks you give score points based on the results.
Finally you will write a short text to summarize the results.

Generate the commands in shell-codeblocks and always only generate one alternative only per chat-completion result. Put every command in a new line. 

## User Change Directory

Fulfill the following tasks:
- Change the current working directory to the home directory.
- Afterwards check in which sub-directory the pom.xml file(s) are stored.

## User Run UnitTests

Your generated commands have been executed and the console output is as follows:  
```shell
{{RESULT}}
```

Now perform the following tasks:
1. Change the current working directory to the directory where the pom.xml file is stored.
2. Run Maven with the 'test' goal.

## User UnitTest Results

The Unit-Tests have been executed and the output is now shown to you.

Summarize the total number of tests found, the number of tests succeeded and the number of tests failed.
Finally print the score points, which is the number of succeeded tests, but with a maximum value of 10.

The console output of the "mvn test" command is:  
```shell
{{RESULT}}
```

## User Test REST Endpoints

Now fulfill the following two tasks:
1. send a HTTP GET Request to http://localhost:8081/api/documents and print the full HTTP Response. 
2. send a HTTP POST Request to http://localhost:8081/api/documents/post_document with the README.md file as HTTP Request Body and print the full HTTP Response

Generate all commands at once.

## User REST Test Results

Your generated commands have been executed and the output is now shown to you.

If the output shows, that the HTTP Requests have been sent successfully and have been answered by localhost, then just answer with the word "SUCCESS" in the first line.
If localhost does not answer on HTTP Requests, then just write "FAILED".
If you can't decide if SUCCESS or FAILED explicitly, or if you need another trial, then answer with the word "CONTINUE" in the first line.

In the following line print the score for the REST Tests, which is the sum of the part-scores:
1. if the GET Request was answered successfully, with HTTP 200, 201 or 204, then this part-score is 10 points (otherwise 0)
2. if the POST Request was answered successfully, with HTTP 201 or HTTP 200, then this part-score is 10 points (otherwise 0)

The console output of your generated commands is:  
```shell
{{RESULT}}
```

## User Improve Test REST Endpoints

Your previous suggestions of commands failed to send the HTTP requests.
Try it again using a different approach.

## User Summary

Summarize the outcome of your activities.
Calculate the total score.
