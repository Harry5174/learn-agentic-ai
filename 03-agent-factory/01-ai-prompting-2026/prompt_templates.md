# AI Prompting in 2026 - Reusable Prompt Templates

This document provides a set of structured, professional templates for daily prompting tasks. Copy, adapt, and fill in the placeholders (indicated by square brackets `[...]`) to apply these patterns in your workflow.

---

## 1. Smart Colleague Brief Template
Use this template to onboard the AI to a new task with complete context, constraints, and success criteria (Concept 1).

```text
Role and Objective:
Act as a smart, professional colleague. I want to build/create [describe the main goal].

Current Tech Stack / Frameworks (if applicable):
- [list programming languages, databases, or frameworks]

Project Context:
- Current skill level/expertise: [e.g., Intermediate Python, beginner FastAPI]
- Existing setup/directory structure: [describe or paste relevant file names/tree]
- What I have already tried: [describe previous attempts or notes]

Constraints:
- [Constraint 1: e.g., Keep the first version simple, do not use external CSS]
- [Constraint 2: e.g., Limit runtime dependencies]
- [Constraint 3: e.g., Do not write placeholders; write complete, functional code]

Expected Output:
Provide:
1. [Output 1: e.g., Architecture design and directory structure]
2. [Output 2: e.g., Complete implementation code for the endpoints]
3. [Output 3: e.g., Step-by-step verification and test commands]
```

---

## 2. Strict Source Web Search Template
Use this template when you require current information and want to prevent the model from citing unverified blogs, forums, or outdated articles (Concept 3).

```text
Search the web for the latest information on [Topic/API/Library].

Allowed Sources:
- Official documentation
- Primary source materials
- Reputable technical specifications or announcements

Excluded Sources:
- Casual developer forums (e.g., Reddit, Quora)
- Unverified blogs
- Outdated pages older than [e.g., 6 months]

Requirements:
1. Summarize the changes or current state clearly.
2. Cite every load-bearing claim with a direct source link.
3. If a claim cannot be verified using the allowed sources, explicitly mark it as "unverified".
```

---

## 3. Deeper Reasoning & Trade-off Analysis Template
Use this template for architectural, strategic, or high-stakes decisions where you want the model to analyze alternative paths rather than pitching a single solution (Concept 5).

```text
I am choosing between [Option A] and [Option B] for [describe the decision or project].

Context:
- [Context details: e.g., 5 hours/week development time, deployment on a single cloud instance, target audience of 100 users]

Think carefully and perform a step-by-step reasoning analysis before answering.

Output Structure:
1. Trade-offs: Analyze the three most critical trade-offs between these options regarding cost, scalability, and complexity.
2. Recommendation: State which option you recommend for my specific context and provide a clear justification.
3. Tipping Points: Under what specific conditions (e.g., scaling requirements, budget changes) would your recommendation flip?
```

---

## 4. Rubric Self-Critique & Autonomous Improvement Template
Use this template to force the model to score its draft, identify missing elements, and iteratively improve the output (Concept 6/13).

```text
Critique the draft provided below using the following criteria. Score each criterion from 1 to 10 with a one-sentence justification.

Draft:
[Paste your draft here]

Criteria:
1. Clarity: Is the main argument or purpose immediately obvious?
2. Structure: Is the content presented in a logical, step-by-step progression?
3. Conciseness: Are there redundant sentences or fluff that can be removed?
4. Evidence/Feasibility: Are claims supported by reasoning or evidence?

For each score:
- Provide the score and justification.
- State the specific modification that would raise the score by at least one point.

After completing the critique, revise the draft incorporating all proposed improvements.
```

---

## 5. Brainstorm-Iterate Loop (Round 1 Template)
Use this template to begin a brainstorming sequence without letting the model produce long, unmanageable essays of text early in the process (Concept 7).

```text
I want to brainstorm ideas for [describe the task: e.g., a portfolio project, a technical article, a database schema].

My background and constraints:
- [Detail 1: e.g., Intermediate developer]
- [Detail 2: e.g., Target duration is 1 week]

Task:
Provide 5 distinct ideas/options.
Keep each option to exactly one line.
Do not expand on them or write introductory/concluding remarks yet.
```

---

## 6. Multi-Model Adjudication Template
Use this template when bringing feedback from a secondary model back to your primary model to reconcile differences (Concept 13).

```text
I ran my current draft through an independent model from a different family, and it generated the following critique.

Draft:
[Paste current draft]

Critique:
[Paste feedback from the second model]

Task:
1. Evaluate each point in the critique.
2. State whether you agree or disagree with the point, providing a brief technical reason.
3. Revise the draft, adopting the agreed-upon points and maintaining the original constraints.
```

---

## 7. Verifiable Data Analysis Brief Template
Use this template when analyzing structured datasets (CSV, JSON) to ensure the model does not guess calculations (Concept 10).

```text
I have provided the dataset [paste data or upload file].

Task:
Analyze this data to identify [describe target: e.g., sales trends, anomaly distribution].

Before performing the analysis, execute a code block to retrieve and output:
1. Total row and column count.
2. Data types of each column.
3. Summary of missing values.

Important:
- Write and run Python code to perform all calculations (averages, medians, trends).
- Show the complete code blocks used for calculations.
- Present the final numbers determined by the code, along with any relevant charts or structured tables.
```
