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
    PROMPT_SYSTEM[Prompt: System] --> ASSIGN_CD

    ASSIGN_CD[Assign: User CD] --> CALL_COTH_CD
    CALL_COTH_CD[[../coth.wf.md]] --> ASSIGN_TEST

    ASSIGN_TEST[Assign: User Test] --> CALL_COTH_TEST
    CALL_COTH_TEST[[../coth.wf.md]] --> EXECUTE_START

    EXECUTE_START[Execute: mvn spring-boot:start > /dev/null] --> ASSIGN_REST
    ASSIGN_REST[Assign: User REST] --> CALL_COTH_REST
    CALL_COTH_REST[[../coth.wf.md]] --> EXECUTE_STOP
    EXECUTE_STOP[Execute: mvn spring-boot:stop > /dev/null] --> PROMPT_SUMMARY

    PROMPT_SUMMARY[Prompt: User Summary] --> SUCCESS
    SUCCESS@{ shape: stadium  }
```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

Your special task will be to use the Maven tool to run the tests of the provided java software project, start the application, perform REST tests, and stop the application. For every tasks you give score points based on the results.
Finally you will write a short text to summarize the results.

## User CD

Fulfill the following tasks:
1. Check in which sub-directory of the home directory the pom.xml file(s) are stored. 
2. Change the current working directory to the directory where the pom.xml file is stored (in order to enable Maven to find the pom.xml file).

## User Test 

Fulfill the following tasks:
Run Maven with the 'test' goal. Summarize the total number of tests found, the number of tests succeeded and the number of tests failed. Finally print the score points, which is the number of succeeded tests, but with a maximum value of 10.

## User REST

Fulfill the following tasks:
1. Send a HTTP GET Request to http://localhost:8081/api/documents and print the full HTTP Response. If the GET Request was answered successfully, with HTTP 200, 201 or 204, then this part-score is 10 points (otherwise 0)
2. Send a HTTP POST Request to http://localhost:8081/api/documents/post_document with the README.md file as HTTP Request Body and print the full HTTP Response. If the POST Request was answered successfully, with HTTP 201 or HTTP 200, then this part-score is 10 points (otherwise 0).

## User Summary

Summarize the outcome of your activities.
Calculate the total score (maximum score is 30)
