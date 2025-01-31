# AI CodeMentor - Tutorials

## Getting started with AI CodeMentor

* To write your own workflow - that is to create your own application with AI-Agents - you just need to write Markfown files and put them into the [/workflows](../../workflows/) directory.  
If you need to learn Markdown, you may want to use this tutorial: https://www.markdownguide.org/getting-started/

* The control-flow is also defined within that Markdown file, using the Mermaid plugin, which renders the text-definition into an easy to read and understand grafik.  
You want to learn more about Mermaid? You may use: https://mermaid.js.org/syntax/flowchart.html

### Lesson 1: Your first Workflow

Let's have a look at a sample of a simple, straight-forward sample to get to know the format in which an AI CodeMentor compatible Markdown file has to be written.
- See the full source file: [workflows/tutorial/lesson1.wf.md](../../workflows/tutorial/lesson1.wf.md)
- Because the Markdown file MUST follow a fixed structure, the file extension is ```.wf.md```

![Lesson 1 - Workflow File Structure](lesson1-workflow-structure.png)

The file contains of the following sections:
- **Title**: Any title which is defined at the first header-1 (```#```) section  
    Sample: "Lesson 1 - 42"
- **Description**: Any markdown which describes the Workflow. The description is optional and will not be used by CodeMentor.  
    Sample: "AI CodeMentor Tutorial: ..."
- **Workflow**: The header-1 section named "Workflow" (```# Workflow```) depicts the section, in which the activities will be defined as Flow-Chart Diagram
- **Workflow Definition** (using Mermaid FlowChart Diagram):  
    In this sample the workflow consist of the following four steps, which are to be executed in a linear flow from START zu SUCCESS, one activity after annother
    1. **START** - The START Activity MUST exist in every workflow with exactly that definition. It is the starting-point for the AI CodeMentor when executing the Workflow.  
    The START activity is connected to the next activity using "-->" named PROMPT_SYSTEM
    2. **PROMPT_SYSTEM** - All Activities whos name starts with "PROMPT_" are activities which will send a prompt to an agent. The caption of this activity MUST start with "Prompt: " also. This activity will set the system prompt of the AI-Agent. The PROMPT_SYSTEM activity is connected to the next activity named PROMPT_ASK.
    3. **PROMPT_ASK** - This activity starts with "PROMPT_" so it is also a prompting activity. Here a user prompt named "User Ask" (this is the string right to "Prompt: " in the caption) which is loaded from the prompt definitions below. This activiy leads to the next activity "SUCCESS".
    4. **SUCCESS** - The SUCCESS Activity finished a workflow and MUST be defined exactly as in the example.
- **Prompts**: The header-1 section named "Prompts" (```# Prompts```) starts the section, in which the prompts used in the workflow are defined. This is a section on its own, because the Prompts may be longer as to be able to show directly in the flow-chart.
- Multiple **Prompt Definition**s  
    In this sample two prompts are defined:
    1. **A System Prompt** (```## System```) - is used to create a new AI-Agent and set the system context of it
    2. **A User Prompt** with the title "Ask" (```## User Ask```) - User Prompts must start with ```## User ``` and have a title which is added right hand side.


Now try it out! From the project directory run:

on Windows:
```shell
bin\run_codementor.ps1 workflows/tutorial/lesson1.wf.md
```
on Linux:
```shell
bin\run_codementor.ps1 workflows/tutorial/lesson1.wf.md
```

The output will be something similar to:
```
The answer to life, the universe, and everything is famously stated as "42" in Douglas Adams' science fiction series "The Hitchhiker's Guide to the Galaxy." This humorous response has become a popular cultural reference, symbolizing the search for meaning in life.
```

Congratulations! You've achieved the first step.

### Lesson 2: Let the AI-Agent execute your first commands

- See the full source file: [workflows/tutorial/lesson2.wf.md](../../workflows/tutorial/lesson2.wf.md)

### Lessons 3: Use iterations for the AI-Agent to improve its result

- See the full source file: [workflows/tutorial/lesson3.wf.md](../../workflows/tutorial/lesson3.wf.md)
