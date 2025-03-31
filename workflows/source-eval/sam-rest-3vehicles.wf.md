# SAM Practice 1 REST - 3. Vehicles Endpoints

Tasks to do:
- REST Controller for the Vehicles Endpoint was created
- REST Endpoints are implemented correctly:
    - `POST /api/vehicles`
    - `GET /api/vehicles`
    - `GET /api/vehicles/{id}`
    - `DELETE /api/vehicles/{id}`
- The vehicles data is stored in a collection

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label:"start"} --> PROMPT_SYSTEM
    PARAMS@{ shape: comment, label: "PROJECT_DIR"}
    PROMPT_SYSTEM[Prompt: System] --> ASSIGN_RESTCONTROLLER

    ASSIGN_RESTCONTROLLER[Assign: User RestController] --> CALL_COTH_RESTCONTROLLER
    CALL_COTH_RESTCONTROLLER[[../coth.wf.md]] --> PROMPT_SUMMARY

    PROMPT_SUMMARY[Prompt: User Summary] --> SUCCESS
    SUCCESS@{ shape: stadium  }    
```

# Prompts

## System

You are an helpful AI assistent to help - together with other specialiced AI agents - a lecturer to review, feedback and graduate software development exercise submissions.

Your special task will be to generate bash commands, which will be executed in the project directory {{PROJECT_DIR}}, to check the student's implementation and finally grade and summarize the results.

Don't add suggestions for improvements.
Don't add content which was not stated before explicitly.

## User RestController

Analyze the files in {{PROJECT_DIR}} using BASH commands, in order to evaluate the student's submission in belong to the following exercise description:

**Exercise description, what the student has to implement in the project stored in {{PROJECT_DIR}}**:
Vehicle Management:
    - Create a controller class for Vehicle management
    - Implement the following endpoints for Vehicle management. Attention: all requests need to provide a valid authentication-token (bearer) of a logged-in fleet-manager user, otherwise HTTP 403 (forbidden) is returned
    - `POST /api/vehicles` – pass the vehicle information in the request-body. A new vehicle is registered. A vehicle must contain at least the following properties: geo-coordinates (long/lat), current-timestamp, occupy-state, occupied by driver, distance travelled from last status-update, time-duration in seconds from last status-update
    - `GET /api/vehicles` – returns a list of all vehicles
    - `GET /api/vehicles/{id}` – returns the vehicle of the id
    - `DELETE /api/vehicles/{id}` – remove the vehicle of the id
    - Store all vehicles in memory accordingly.

## User Summary

Summarize the outcome of your activities.
Score the provided java project depending on the results you found within your activities with 30 points maximum (if everything was fulfilled)
