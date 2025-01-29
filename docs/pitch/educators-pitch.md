---
marp: true
title: AI CodeMentor - Automating the Evaluation of Programming Assignments
description: Enhancing Assessment Efficiency with AI-driven Workflows
author: Bernhard Wallisch (bernhard_wallisch@hotmail.com)
keywords: AI-Agents, AI autonomy, CodeMentor, AI, Software Programming, Education
url: https://github.com/BernLeWal/AICodeMentor
theme: gaia
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
footer: 'AI CodeMentor: Automatic the Evaluation of Programming Assignments'
---
<style>
section { 
    font-size: 28px; 
}
</style>
<!--
_paginate: skip
_footer: ''
_class : lead
-->

# AI CodeMentor – Automating the Evaluation of Programming Assignments

Enhancing Assessment Efficiency with AI-driven Workflows

Bernhard Wallisch ([https://github.com/BernLeWal](https://github.com/BernLeWal))

<!-- 
Welcome, and thank you for attending this presentation on AI CodeMentor. Today, I'll introduce an AI-driven approach to grading programming assignments, discuss its advantages, and explore the broader implications of AI in education.
-->
---
<!-- Introduction -->
## The Challenge of Assessing Programming Assignments

* University courses often require evaluating **hundreds of programming submissions**.
* Manual grading is **time-consuming** and **limits student feedback**.
* Traditional automated assessment tools exist but have limitations:

    - **Too formal** – rigid structures stifle student creativity.
    - **Require programming skills** – difficult for non-developers to configure.
    - **High entry barriers** – adoption by educators remains low.

* **How can AI help?**

<!--
As educators, we often face the challenge of evaluating hundreds of programming submissions per semester. Traditional grading methods are either highly manual or rely on rigid rule-based systems. The issue is that such systems limit student creativity and are difficult to maintain. AI presents a potential solution—let’s explore how.
-->
---
<!-- Evolution of Automated Evaluation -->
## From Rule-Based Systems to AI-driven Assessment

* **Traditional Approach** (Static-/Rule-Based Systems):
    - Works best for structured, predictable assignments.
    - Requires constant **manual maintenance and rule updates**.
    - **Not flexible enough** for creative solutions.

* **AI-Augmented Approach** (AI CodeMentor):
    - Uses **autonomous AI agents** to interpret and evaluate code.
    - Provides **adaptive feedback** and **iterates** for better results.
    - Offers **higher-level abstraction** for defining evaluation workflows.

<!--
The standard automated grading approach works well when submissions follow a fixed format. However, students often approach problems in different ways, making rigid rules inadequate. AI CodeMentor aims to provide a more adaptive, intelligent system that can interpret and assess code flexibly.
-->
---
<!-- AI CodeMentor - How it works -->
## AI CodeMentor in Action

![bg width:450px right:35%](../Screenshot_run_workflow.png)

* **Workflow-Driven Evaluation**:

    - Evaluation logic is defined in Markdown workflows (.wf.md).
    - Workflows specify grading criteria, test cases, and expected outputs.

* **AI Agents Execute and Analyze**:

    - AI agents generate **shell commands** to run tests.
    - Commands are executed in an **isolated environment** (Docker container).
    - AI agents analyze **results, logs, and errors** to improve assessment evaluation.
<!--
At its core, AI CodeMentor is a workflow-driven evaluation tool. Educators define grading workflows in Markdown, specifying criteria and tests. AI agents execute and analyze code, iterating when necessary. This process reduces manual grading effort while offering detailed feedback.
-->
---
<!-- Hands-On Demo -->
## Live Demonstration of AI CodeMentor

**1. Step**: Define the grading process as a **Markdown workflow**.
**2. Step**: Run AI CodeMentor in verbose mode to **observe execution**.
**3. Step**: Demonstrate how AI **traces results** through multiple workflow stages:

    - Sprint1.wfh → Sprint1.musthaves.wfh → Sprint1.testing.wfh

**4. Outcome**: See how AI autonomously evaluates and iterates on student submissions.
<!--
Now, let’s see AI CodeMentor in action. I'll walk you through a workflow definition, the runtime execution, and how AI traces multiple stages of evaluation. You'll observe how it autonomously evaluates and improves assessments.
-->
---
<!-- Key Benefits -->
## Why AI CodeMentor?

* **Greater flexibility** – accommodates diverse student solutions.
* **Reduced grading workload** – automates tedious evaluation steps.
* **Enhanced student feedback** – AI suggests improvements in real-time.
* **Scalable & adaptable** – can evaluate hundreds of submissions simultaneously.
<!--
So, why use AI CodeMentor? The main benefits are flexibility, automation, real-time feedback, and scalability. It reduces grading workloads while providing richer insights into student performance.
-->
---
<!-- Open Questions -->
## The Broader Implications of AI in Education

* **Ethical Considerations**:

    - Should AI play a role in grading students?
    - How do we ensure fairness and transparency?

* **Educational Impacts**:

    - Will AI grading influence how students learn and code?
    - What role should educators play in AI-assisted assessment?

* **The Future of AI in Learning**:

    - How can AI enhance personalized learning?
    - Where do we draw the line between automation and human oversight?
<!--
However, this raises important questions. Should AI be grading students? How do we ensure fairness and prevent bias? How will AI-assisted learning impact student development? These are discussions we need to have as AI continues to evolve.
-->
---
<!-- Conclusion -->
## AI CodeMentor – A Discussion, Not a Final Solution

- Not a commercial product – a prototype for exploration.
- Designed to spark discussion among educators, researchers, and technologists.
- No fixed answers, but important questions about the role of AI in education.
- Looking forward to your thoughts and feedback!
<!--
To be clear, AI CodeMentor is not a final solution—it's an exploration. It’s designed to spark discussion among educators and researchers about AI’s role in education. I encourage you to share your thoughts and concerns
-->
---
<!--
_paginate: skip
_footer: ''
_class : lead
-->
# Thank You for Your Attention!

**Questions & Discussion**

Contact: [bernhard_wallisch@hotmail.com](mailto:bernhard_wallisch@hotmail.com)

GitHub Repository: [https://github.com/BernLeWal/AICodeMentor](https://github.com/BernLeWal/AICodeMentor)
<!--
That concludes my presentation. Thank you for your time! I'm happy to take any questions
-->