# Reflections on AI Prompting in 2026

## Introduction
The methods taught in the "AI Prompting in 2026" course represent a fundamental shift in user capability. This document reflects on the core transitions in cognitive habits, validation disciplines, and workflow systems required to use LLMs as professional thinking and working partners.

---

## 1. The Shift from Producing to Evaluating
Historically, a professional's primary output was content generation: drafting reports, writing code, formatting spreadsheets, and summarising data. With the maturity of AI-native tooling, the cost of content generation has decreased significantly. 

*   **The Paradigm Shift**: The bottleneck is no longer production capacity, but evaluation capability. 
*   **The Challenge**: A power user must transition from being a writer or coder to an editor and critic. They must define the quality criteria (rubrics) and verify the outputs, rather than writing the text or code. If the user cannot spot logical contradictions, subtle bugs, or shallow arguments, the final output will be mediocre.

---

## 2. The 10-80-10 Operating Rhythm in Prompting
The 10-80-10 rhythm is not only an organizational structure for large-scale agent factories; it is a discipline for individual prompts.

*   **The Initial 10% (Context Engineering)**: Instead of firing off a quick query, the user spends time building a robust brief. This involves collecting the necessary files, setting constraints, defining output formats, and selecting the correct retrieval mode (Concept 1, 3, 4).
*   **The Middle 80% (Autonomous Processing)**: The model processes the instructions, utilizing features like thinking traces, sandboxed code execution, or multi-model critique. The user steps back, allowing the model to perform the heavy analytical lift.
*   **The Final 10% (Systematic Verification)**: The user evaluates the output. They run tests, click prototypes, cross-check links against source documents, and use secondary models to check for blind spots (Concept 13).

---

## 3. Confronting Sycophancy and the "Looks Right" Trap
AI models are optimized to please the user, which often leads to sycophancy. The model will validate incorrect assertions, praise mediocre plans, and confirm broken code if the user's prompt signals a preferred outcome.

*   **The Solution**: A power user must actively engineer prompts that demand critique rather than confirmation (Concept 6).
*   **The Rubric Method**: By forcing the model to score its own draft against specific, named criteria (1-10) and detail exactly what is required to raise each score, the user turns the model's output into a objective feedback loop. Without a rubric, self-critique defaults to shallow praise.

---

## 4. Silent Failure Modes and the Need for Verification
The most dangerous failure modes in 2026 are not obvious errors or wild hallucinations, but silent failures.

*   **The Data Analysis Trap**: When asked to calculate statistical values (medians, averages, outliers) from a list of numbers, a model will often output a confident paragraph containing incorrect calculations without running code. It relies on its token-prediction probability, which is fundamentally unsuited for math.
*   **The Discipline**: The user must explicitly command the model to write and execute code in a sandboxed environment to process data, and then verify that the code block actually ran. This discipline represents the difference between guessing and verifying.

---

## Conclusion
Advanced prompt engineering is not about learning static phrases or tricks. It is about establishing a personal operating system of context management, framing discipline, and rigorous verification. As models evolve and integration deepens, these cognitive habits remain the constant factor in achieving high-quality results.
