# AI Code Mentor

**AI Code Mentor** is an extensible, containerized **runtime environment** for executing **autonomous AI agent workflows**. It is tailored for developers, researchers, and power users who seek to harness generative AI for complex, multi-step reasoning tasks, automation scenarios, or AI-assisted evaluations.

Each application is defined as a **Markdown-based workflow** (*.wf.md) and executed by the Code Mentor engine. These structured workflows allow one or more AI agents to iteratively analyze, reason, generate, and execute shell commands—autonomously or in coordination. Each command’s output is re-evaluated in context, enabling **self-refinement** and adaptive problem-solving through autonomous loops.

At the core of AI Code Mentor is a modular, pluggable architecture. Currently integrated are various cloud-platform tools, like OpenAI, Google Gemini, Anthropic Claude (with OpenAI's platform as default setting) and Huggingface Transformer based LLMs which can be executed self-hosted. The system is designed for future extensibility, including support for additional model providers and self-hosted LLMs.

The Docker image is built from the official open-source implementation on GitHub:
🔗 https://github.com/BernLeWal/AICodeMentor
You will find detailed technical documentation, workflow specifications, and developer guides there.

## Key Features
- 🧠 **Multi-agent orchestration** for cooperative AI tasks
- 📜 **Workflow-as-code**: Define actions and logic in Markdown
- 🔁 **Autonomous iteration** with feedback loops and re-evaluation
- 🧩 **Extensible architecture** for integrating diverse AI backends
- 🔐 **API-key based model access** (OpenAI GPT-4, GPT-4o, etc.)
- 🐳 **Ready-to-run Docker image** with no installation overhead
- 📂 **Workflow examples included**, covering real-world applications (see [AICodeMentor/workflows](https://github.com/BernLeWal/AICodeMentor/tree/main/workflows) for a full list)

## Getting Started
To execute a sample workflow, use the provided container and set your OpenAI API key as an environment variable.

Below is an example of how to launch a container that runs the included `prompt-eval` workflow. This evaluates the quality of a user-defined prompt using principles of prompt-engineering:

```bash
docker run --rm \
  -e OPENAI_API_KEY=sk-yourkeyhere \
  codepunx/codementor \
  workflows/prompt-eval/prompt-eval.wf.md \
  USER_PROMPT="You are a helpful AI assistant in the area of education to support lecturers in creating course evaluation systems. The generated output should be formal. Your task is to put together a short list of characteristica, which can be used when evaluating user prompts regarding the best practices for high quality generative-AI tool output."
```
For more advanced usage patterns—such as creating custom workflows, configuring agent behavior, or integrating with local models—please refer to the documentation on GitHub.

## Learn More

### 📘 Documentation
Explore tutorials, configuration options, and developer guidelines:
https://github.com/BernLeWal/AICodeMentor/tree/main/docs

### 💡 Examples & Use Cases
Browse ready-made workflows and real-world scenarios in the workflows/ directory.

### 🤝 Contribute
AI Code Mentor is open to contributions. New features, AI backends, or workflow enhancements are welcome.

## AI Code Mentor – Build Smarter, Iterate Faster.
Containerized intelligence to empower your automation and AI development pipelines.