# Plan Like a Graph (PLaG)

The technique "Plan Like a Graph" (PLaG) allows dependencies and sequences in planning steps to be initially represented as directed acyclic graphs (DAGs). This helps traditional language models better utilize the capabilities of the OpenAI o1 reasoning model family, not only in synchronizing tasks but also in planning more precisely which steps need to be executed in parallel and which must follow one another.

In their own benchmark, the research group has shown that the accuracy of planning tasks significantly improves with the use of PLaG. However, this also leads to longer outpus (and thus higher token consumption) for models, similar to inference sequences, which translates into higher costs for (cloud) API-based use.

As a result, the models can create a hierarchical visualization, even if the input data does not fully describe a suitable sequence for the used layer model.

Despite improvements through PLaG, the study shows that language models still encounter challenges with complex tasks, emphasizing the need to carefully verify the obtained results. The researchers remain skeptical about further developments in reasoning language models and agent systems to address this issue more effectively.

References: 
- iX Artikel (vom 03/2025): [Prozessvisualisierung mit generativer KI im Praxistest](https://www.heise.de/select/ix/2025/3/2430310385032261248)
- Paper: [Graph-enhanced Large Language Models in Asynchronous Plan Reasoning](https://arxiv.org/pdf/2402.02805)
- Github Repo used by the paper: [fangru-lin/graph-llm-asynchow-plan](https://github.com/fangru-lin/graph-llm-asynchow-plan)

---

# Ideas

- use the "Making a breakfast" example from [Microsoft: Asynchronous programming with async and await](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/) for an implementation scenario