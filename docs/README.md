# CodeMentor Software Documentation

Table of contents:
- [AI Agent System](agents.md)
- [Command Parsing & Execution](commands.md)
- [Workflow Definition & Interpretation](workflow.md)

## Architecture

The architecture in that software is built around AI-Agents to fulfil the required tasks and work as an autonomous AI-Agend as defined in [*Agents* pblished by Google](https://media.licdn.com/dms/document/media/v2/D561FAQH8tt1cvunj0w/feedshare-document-pdf-analyzed/B56ZQq.TtsG8AY-/0/1735887787265?e=1736985600&v=beta&t=pLuArcKyUcxE9B1Her1QWfMHF_UxZL9Q-Y0JTDuSn38)

* **Cognitive Architecture**: *This refers to the foundational framework of an AI agent that guides how it processes information, makes decisions, and takes actions. It consists of components like reasoning techniques, planning capabilities, and memory.*  
CodeMentor uses Platform OpenAI and other LLMs, see module [/app/agents/](../app/agents/)

* **Orchestration Layer**: *This layer is central to an AI agent's cognitive architecture, as it manages how the agent processes inputs, reasons through tasks, and decides on its next actions. It allows the agent to maintain context, track progress, and execute tasks in a logical sequence until its objective is achieved.*
This is implemented in the WorkflowInterpreter, see module [/app/workflow/](../app/workflow/)

* **Extensions**: *These are tools that allow AI agents to interact with external systems, such as APIs, in a structured way. Extensions enable agents to perform tasks like retrieving live data or sending commands, bridging the gap between the agent's internal capabilities and the outside world.*  
The external system currently used is a docker container equiped with a BASH shell, and may be extended to further systems in future. For the integration see module [/app/commands/](../app/commands/)

* **Functions**: *Functions are predefined modules that the agent can use to complete specific tasks. Unlike extensions, which operate on the agent side, functions run on the client side, giving developers more control over execution while letting the agent determine when and how to use them.*  
The input from the user is coming from the workflow-definition which is a flow-design of the work to be proceeded with prompt-templates used. In future an interactive console between the AI-Agent and the user will be able to be used within the workflow process.
