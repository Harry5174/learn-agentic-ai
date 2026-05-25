# AI Prompting in 2026 - Notes

## Part 1: How AI Knows Things

### Concept 1: Novice vs Power User

**Understanding**  
A novice tends to ask short, simple prompts. In contrast, a power user provides rich context—like background information, constraints, relevant files, examples, and a clear idea of the expected output.

**Why It Matters**  
The same AI model can deliver much better answers when it’s properly briefed. The quality of the prompt directly influences the quality of the response.

**How to Apply**  
Before asking AI for help with any project, I’ll make sure to provide:  
- The project goal  
- The current tech stack  
- The folder structure I’m working with  
- The exact error or problem I’m facing  
- What I expect as an output  
- Any constraints or limitations  

---

### Context Management

- AI models don’t remember past sessions—they’re stateless. Each interaction re-injects only a few facts into the context.  
- Every prompt engineering technique is essentially about filtering out irrelevant context and including the right context.

---

### Concept 2: Pretrained Knowledge

**Understanding**  
- Large language models (LLMs) memorize terabytes of training data.  
- Some of this knowledge might be outdated or even incorrect.  
- The more frequently a concept appears in training data, the more reliable the model’s knowledge about it.

**Why It Matters**  
- When pretrained knowledge is less reliable, you need to supply more explicit information in your prompt.

**How to Apply**  
- Categorize the knowledge you need. The rarer or more specialized the knowledge, the more explicit and detailed your prompt should be.

---

### Concept 3: The Three Retrieval Modes: Pretrained, Web Search, Deep Research

**Understanding**  
AI models decide whether to use pretrained knowledge, web search, or deep research based on the prompt. But users can guide this choice by crafting better prompts tailored to the task.

**Why It Matters**  
- Each retrieval mode has different costs, latencies, and strengths.  
- By choosing the right mode, users can optimize for speed, accuracy, or depth.

**How to Apply**  
- Use pretrained knowledge for common, well-known tasks.  
- Use web search when you need recent or up-to-date information.  
- Use deep research for complex, nuanced tasks that require thorough investigation.
