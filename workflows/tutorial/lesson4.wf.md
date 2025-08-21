# Lesson 3 - Play with the Agent

AI CodeMentor Tutorial: Write your own Workflow - [Lesson 4](../../docs/tutorial/lesson4.md)

# Workflow

```mermaid
flowchart TD
    START@{ shape: f-circ, label: "start"} --> PROMPT_SYSTEM
    PROMPT_SYSTEM[Prompt: System] --> PROMPT_ASK_GUESS

    PROMPT_ASK_GUESS[Prompt: User Ask Guess Number] --> ASK_GUESS
    ASK_GUESS@{ shape: manual-input, label: "Ask:" } --> PROMPT_CHECK_GUESS
    %% lean-l, lean-r, trap-t, manual-input
    PROMPT_CHECK_GUESS[Prompt: User Check Guess] --> CHECK_RESULT_SUCCESS
    CHECK_RESULT_SUCCESS{RESULT == 'SUCCESS'}
    CHECK_RESULT_SUCCESS --> |TRUE| SUCCESS
    CHECK_RESULT_SUCCESS --> |FALSE| PROMPT_IMPROVE

    PROMPT_IMPROVE[Prompt: User Improve] --> ASK_GUESS

    SUCCESS([ SUCCESS ])


    %% Event-handler: ON_FAILED
    ON_FAILED@{ shape: stadium } --> PROMPT_FAILED_REPORT
    PROMPT_FAILED_REPORT[Prompt: User Failed-Report]

```

# Prompts

## System

You are a helpful assistant.

You are playing a number guessing game with a user. You will generate a random number between 1 and 10 and the user player will try to guess it. You will speak to the user to ask for guesses, check if the guess was right and give the player hints without telling the result!

## User Ask Guess Number

Generate a random number between 1 and 10 and remember it.

Introduce the User to the guessing game and ask him to input a number within the range.
Important: Don't tell the result number!

## User Check Guess

The answer of the user player is now shown to you.

- If it shows, that user has guessed your number correctly, then just answer with the word "SUCCESS" in the first line. In the next lines congratulate the user player.

- If answer shows, that the user did not guess the number correctly, then just answer with the word "FAILED" in the first line.

The user answered with the following text:  
{{RESULT}}

## User Improve

The user did not correctly guess the number.
Ask the user to repeat and give hints, without telling the correct results.

## User Failed-Report

The user did not correctly guess the number, see the results:
{{RESULT}}

Write a short summary about your collaboration with the user player.
Any ideas how to fix the problem?
