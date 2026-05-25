# AI Prompting in 2026 - Notes

## Source

Panaversity Agent Factory: AI Prompting in 2026

## Course Goal

This course teaches how to use modern AI tools as serious thinking and working partners instead of treating them like simple search engines.

The central idea is:

> Prompting is not about clever wording. It is about controlling context.

Almost every advanced prompting technique is one of two moves:

1. Get the right context into the model.
2. Keep the wrong context out of the model.

Modern AI tools can use pretrained knowledge, web search, deep research, files, images, audio, code execution, and app-building artifacts. The user's job is to brief the AI clearly, choose the right mode, verify the output, and iterate.

---

# Part 1: How AI Knows Things

## Concept 1: Novice vs Power User

### Understanding

A novice uses AI like a search engine. They ask short, vague questions and expect the model to guess the missing context.

A power user briefs AI like a smart but new colleague. They provide:

- background context
- constraints
- relevant files
- examples
- expected output format
- success criteria
- permission to critique or compare options

The same model can produce a weak answer or a strong answer depending on how well it is briefed.

### Why It Matters

The model does not know your situation unless you tell it. A vague prompt leads to generic output. A clear brief leads to useful, specific output.

### Weak Prompt

```text
Build me a RAG app.
```

### Strong Prompt

```text
I want to build a PDF-based RAG chatbot using FastAPI, ChromaDB, and Gemini/OpenAI.

Goal:
The user uploads PDFs, asks questions, and receives answers with source references.

Current skill level:
Intermediate Python, some FastAPI, basic LangChain experience.

Constraints:
- Keep the first version simple.
- Use local file storage first.
- Use SQLite or PostgreSQL for metadata.
- Avoid overengineering.
- Make it deployable later with Docker.

Expected output:
Give me the architecture, folder structure, API endpoints, implementation milestones, and testing plan.
```

### How I Will Apply This

Before asking AI for help with projects, I will include:

* project goal
* current tech stack
* current folder structure
* exact error/problem
* expected output
* constraints
* deployment target
* what I already tried

---

## Concept 2: Pretrained Knowledge

### Understanding

AI models learn from large amounts of text data. They do not experience the world directly. They learn patterns from internet text, books, articles, forums, documentation, and other training sources.

Their pretrained knowledge is strongest when the topic is common, widely discussed, and stable.

Their pretrained knowledge is weaker when the topic is:

* obscure
* local
* recently changed
* private/internal
* disputed
* missing from public data

### Practical Trust Scale

| Question Type                          | Trust Level | Action                               |
| -------------------------------------- | ----------: | ------------------------------------ |
| Common programming syntax              |        High | Use pretrained answer, but test code |
| General explanation of common concepts |        High | Use answer as learning aid           |
| Recent regulations, news, prices, APIs |         Low | Use web search                       |
| Internal company decisions             |    Very low | Provide documents/context            |
| Niche local history or rare topics     |         Low | Verify against primary sources       |
| Medical/legal/financial decisions      |         Low | Use sources and expert review        |

### Why It Matters

A model can sound confident even when the topic was poorly represented in training data. Confidence is not proof.

### How I Will Apply This

Before trusting an answer, I will ask:

```text
How would the model know this?
```

If the answer depends on recent, private, rare, or high-stakes information, I will provide sources or ask for web search with citations.

---

## Concept 3: The Three Retrieval Modes

### Understanding

Modern AI tools can answer using three broad modes:

1. **Pretrained knowledge**
2. **Web search**
3. **Deep research**

The model often chooses automatically, but the user can steer the mode through prompt wording.

### Mode 1: Pretrained Knowledge

Best for:

* definitions
* stable concepts
* common programming knowledge
* general explanations
* well-known books, movies, history, and concepts

Prompt patterns:

```text
Explain X simply.
Summarize Y.
What is the difference between A and B?
```

Risk:

* outdated information
* hallucination on obscure topics
* overconfidence

---

### Mode 2: Web Search

Best for:

* current events
* new tools
* latest documentation
* prices
* recent policies
* laws/regulations
* schedules
* product comparisons

Prompt patterns:

```text
Search the web for the latest information on X.
Use current sources.
Cite each claim.
Flag anything you cannot verify.
```

Risk:

* weak sources
* outdated pages
* popular pages being treated as authoritative
* summaries losing nuance

### Better Web Search Prompt

```text
Search the web for the latest information on [TOPIC].

Use only:
- official documentation
- primary sources
- reputable technical sources

Do not use:
- forums
- random blogs
- outdated pages

Cite each important claim.
If a claim cannot be verified, mark it as "unverified".
```

---

### Mode 3: Deep Research

Best for:

* complex decisions
* multi-source reports
* comparisons
* strategy
* technical landscape reviews
* research-heavy questions

Prompt patterns:

```text
Research this thoroughly.
Use multiple source types.
Produce a structured report with citations.
Compare trade-offs, risks, and recommendations.
```

Risk:

* slower
* overkill for simple questions
* still needs human verification

### How I Will Apply This

I will choose the mode based on the task:

| Task                                             | Best Mode                 |
| ------------------------------------------------ | ------------------------- |
| Learn Python syntax                              | Pretrained                |
| Latest LangGraph changes                         | Web search                |
| Compare agent frameworks for a portfolio project | Deep research             |
| Analyze my uploaded PDF                          | File context + reasoning  |
| Debug my current code                            | Provided code + reasoning |

---

# Part 2: Talking to AI Well

## Concept 4: Context Is the Whole Game

### Understanding

The model only answers from what is inside its current context window.

Context can include:

* system instructions
* tool descriptions
* current prompt
* chat history
* uploaded files
* images
* PDFs
* spreadsheets
* code snippets
* previous messages in the same conversation

The model does not automatically know past conversations, files you did not attach, or constraints you forgot to mention.

### Key Principle

Before sending a serious prompt, ask:

```text
Would a smart new colleague have enough information to do this task well?
```

If not, add the missing context.

### Context Checklist

Before a non-trivial prompt, include:

* What is the task?
* What is the background?
* What constraints matter?
* What files/documents should be followed?
* What output format do I want?
* Who is the audience?
* What should the AI avoid?
* What should count as success?

### Example Prompt

```text
I am working on a FastAPI-based RAG chatbot.

Current stack:
- Python
- FastAPI
- ChromaDB
- Gemini API
- Docker later

Current problem:
The chatbot gives answers but does not cite source chunks clearly.

Goal:
Improve the response format so every answer includes:
1. direct answer
2. supporting source chunks
3. confidence level
4. "not found" response when context is insufficient

Constraints:
Avoid rewriting the whole project. Suggest minimal changes first.

Expected output:
Give me the design, file-level changes, and sample code.
```

---

## Context Rot

### Understanding

Long conversations become noisy. As the chat grows, older details may become less reliable because:

* irrelevant context stays in the conversation
* the model may over-reference old topics
* older messages may be compacted or summarized
* constraints may be forgotten or blurred
* answers may become longer and vaguer

### Symptoms of Context Rot

* AI references unrelated earlier topics.
* It contradicts a constraint from earlier.
* It gives vague, bloated answers.
* It apologizes repeatedly without progress.
* It seems confused about the current task.

### Fix

Start a new conversation when the topic changes.

Keep reusable context in:

* project files
* notes
* README files
* prompt templates
* ChatGPT Projects / Claude Projects / Gemini Notebooks
* GitHub documentation

### My Rule

```text
Chat is working memory, not permanent storage.
Important context belongs in files.
```

---

## Projects / Persistent Workspaces

### Understanding

Modern AI tools provide project-like workspaces where you can front-load context once instead of repeating it in every prompt.

Examples:

* ChatGPT Projects
* Claude Projects
* Gemini Notebooks / NotebookLM

Use projects when you repeatedly provide the same:

* files
* audience description
* writing style
* coding rules
* project goals
* constraints

### How I Will Apply This

For my learning path, I can create a project/workspace for:

```text
Panaversity Agent Factory Learning
```

Standing context:

* I am learning agentic AI.
* I want to build deployable portfolio projects.
* I use Python, FastAPI, RAG, Docker, and GitHub.
* I prefer learning by building artifacts.
* Keep me focused and avoid over-diversification.

---

## Concept 5: Reasoning / "Think Hard"

### Understanding

For harder tasks, modern AI models can spend more time reasoning before answering. This is useful for multi-step, trade-off-heavy, or high-stakes tasks.

Instead of only asking:

```text
Explain this.
```

ask:

```text
Think carefully before answering.
```

or:

```text
Think hard about the trade-offs before giving a recommendation.
```

### Use Thinking Mode For

* architecture decisions
* debugging complex errors
* comparing frameworks
* research planning
* financial trade-offs
* project planning
* career decisions
* multi-agent system design

### Do Not Use Thinking Mode For

* simple definitions
* tiny summaries
* casual brainstorming
* quick syntax questions
* low-stakes answers

### Example Prompt

```text
I am choosing between CrewAI and LangGraph for my next agentic AI portfolio prototype.

Context:
- I already have some experience with CrewAI.
- I want to build deployable projects, not just demos.
- I use Python and FastAPI.
- I care about state, reliability, debugging, and production readiness.

Think hard before answering.

Tell me:
1. The three trade-offs that actually matter.
2. Which one I should use first and why.
3. Under what conditions your recommendation would change.
```

---

## Concept 6: Sycophancy and How to Neutralize It

### Understanding

AI models tend to agree with the user because agreement often receives positive feedback. This can make the model overly supportive even when the user's idea, code, or plan is weak.

Bad prompts accidentally signal the desired answer.

### Sycophancy-Bait Prompts

```text
Don't you think this idea is good?
Confirm that this code is correct.
Find evidence that my strategy will work.
Why is approach A better than approach B?
Tell me my draft is ready.
```

These prompts push the model toward agreement.

### Neutral Rewrites

| Weak Prompt                   | Better Prompt                                                     |
| ----------------------------- | ----------------------------------------------------------------- |
| Confirm this code is correct. | Find bugs, edge cases, and unstated assumptions in this code.     |
| Why is A better than B?       | Compare A and B on cost, risk, speed, and maintainability.        |
| Find evidence this will work. | Evaluate this strategy. List arguments for and against.           |
| Tell me my draft is ready.    | Score this draft on clarity, structure, evidence, and usefulness. |
| Defend my decision.           | Give me the strongest counterargument to my decision.             |

### Rubric Pattern

A rubric forces the model to evaluate instead of praise.

```text
Evaluate this project idea using the following criteria.

Score each from 1 to 10 with a one-sentence justification:
1. Real problem
2. Market/user need
3. Technical feasibility
4. Portfolio value
5. Deployment feasibility
6. Risk of overengineering

Then tell me the single change that would raise each score the most.
```

### My Rule

Use verbs like:

* evaluate
* compare
* critique
* find flaws
* list both sides
* score
* identify assumptions

Avoid verbs like:

* confirm
* prove
* defend
* support
* validate

---

## Concept 7: The Brainstorm-Iterate Loop

### Understanding

AI's first answer is usually average because it reflects common patterns from the internet. The way to get better results is not one magic prompt. It is a loop.

### The Loop

1. Load context.
2. Ask for 3–5 options.
3. Do not expand yet.
4. Give explicit feedback.
5. Ask for revised options.
6. Repeat 2–3 rounds.
7. Choose one option.
8. Expand only after the structure is good.
9. Grade the output.
10. Improve until the score plateaus.

### Why It Matters

Most leverage happens before the final draft or final plan. If the outline or direction is wrong, polishing the final answer wastes time.

### Example: Project Ideas

Round 1:

```text
I want to build a small deployable AI worker project.

Context:
- I know Python, FastAPI, RAG, Docker basics.
- I want portfolio value.
- I can spend 5 hours per week.
- I want something useful but not overengineered.

Give me 5 project ideas.
One line each.
Do not expand yet.
```

Round 2:

```text
I reject options 2 and 4 because they are too broad.
I like option 1 because it connects to my RAG background.
I want it to be deployable with a small FastAPI backend.

Give me 5 revised options in that direction.
```

Round 3:

```text
I choose option 3.

Now expand it into:
- problem statement
- user flow
- architecture
- folder structure
- API endpoints
- database tables
- testing plan
- deployment plan
```

### My Rule

Do not ask for the final output too early.

First:

```text
options → feedback → revised options → outline → critique → expand → grade → improve
```

---

# Part 3: Beyond Text

## Concept 8: Multimodal AI - Images, Audio, and More

### Understanding

Modern AI is not limited to text. It can work with:

* images
* screenshots
* whiteboards
* handwritten notes
* PDFs
* audio recordings
* voice input
* generated images
* diagrams

### Image Input Is Good For

* understanding overall scenes
* reading clear whiteboards
* transcribing handwritten notes
* extracting information from screenshots
* summarizing diagrams
* combining multiple visual notes

### Image Input Is Weak For

* counting many small objects
* reading tiny text
* fine-grained visual details
* blurry images
* high-stakes OCR without checking

### Useful Prompt for Images

```text
Analyze this image.

Tasks:
1. Describe what is visible.
2. Extract any readable text.
3. Summarize the main information.
4. Flag anything uncertain.
5. Do not guess small unclear details.
```

### Audio Input Is Good For

* long-form dictation
* meeting summaries
* brainstorming while walking
* voice notes
* turning spoken thoughts into structured text

### Meeting Transcript Prompt

```text
Summarize this meeting transcript.

Output:
1. Decisions made
2. Open questions
3. Action items by owner
4. Risks or blockers
5. Follow-up message draft

Flag anything unclear instead of guessing.
```

### How I Will Apply This

For learning and portfolio building:

* use voice notes to explain concepts in my own words
* ask AI to clean them into notes
* upload diagrams/screenshots for explanation
* use image input for UI/design feedback
* use multimodal prompts when text alone is not enough

---

## Concept 9: Building Small Apps with One Prompt

### Understanding

Modern AI tools can generate small interactive apps directly inside the chat interface. These are useful for simple tools, demos, and prototypes.

The basic prompt structure is:

```text
Goal:
Input:
Output:
```

### Best For

* one-screen apps
* calculators
* timers
* simple games
* dashboards
* quizzes
* small visual tools
* prototypes

### Hard For

* full production apps
* authentication
* multiplayer
* complex backend systems
* payment systems
* large databases
* real-time AI tutors
* multi-service architectures

### Example Prompt

```text
Build a small interactive app.

Goal:
Help me practice prompt engineering concepts.

Input:
The app shows a scenario and I type a prompt.

Output:
The app scores my prompt from 1-10 on:
- context
- clarity
- constraints
- output format
- verification

Then it gives one improvement suggestion.

Style:
Clean, minimal, dark mode.
```

### How I Will Apply This

I can use one-prompt apps to create small learning tools, but for portfolio-grade projects I should later rebuild them properly with:

* Python/FastAPI
* database
* tests
* README
* deployment

---

## Concept 10: Data Analysis - The Model Writes and Runs Code

### Understanding

For math, spreadsheets, charts, and data analysis, the AI should not guess. It should write and run code.

This is more reliable because the computation is done by code, not by the model's internal text prediction.

### Silent Failure Mode

Sometimes the model answers a data question without actually running code. The response may sound confident but be wrong.

### Fix

Ask explicitly:

```text
Write and run code to answer this.
Show me the code you ran.
Before analysis, report:
- row count
- column names
- date range
- missing values
```

### Good Data Prompt

```text
I uploaded a CSV file.

Task:
Analyze the data and identify the most important trends.

Before analysis:
1. Tell me the row count.
2. Tell me the column names.
3. Tell me the data types.
4. Tell me whether there are missing values.
5. Tell me what each column seems to represent.

Then:
- write and run code
- show the code
- create charts where useful
- explain insights in plain English
- flag assumptions
```

### What to Double-Check

* final totals
* graph labels
* date parsing
* misunderstood columns
* missing values
* whether code actually ran
* whether the chart supports the written explanation

### How I Will Apply This

For future projects, I can use AI data analysis to:

* evaluate RAG results
* analyze prompt scores
* compare model outputs
* create GitHub learning progress charts
* inspect logs from deployed AI workers

---

# Part 4: Working Safely and Choosing Tools

## Concept 11: AI Desktop Apps and Permissions

### Understanding

AI desktop apps can access files and perform actions on a computer with permission. This can be powerful but risky.

They can:

* search folders
* organize files
* rename files
* summarize project folders
* edit documents
* act on local files

### Safety Workflow

Never allow action immediately.

Use this workflow:

1. Tell it the task.
2. Ask for a plan only.
3. Review the plan.
4. Edit the plan.
5. Approve execution only after review.

### Safe Prompt

```text
Look through this folder and propose an organization scheme.

Important:
- Do not move files.
- Do not rename files.
- Do not delete files.
- Only show me the proposed folder tree.
- Flag files you cannot classify confidently.
```

### Permission Ladder

| Stage                  | Allow                                 | Avoid                  |
| ---------------------- | ------------------------------------- | ---------------------- |
| First use              | Read-only access to one small folder  | Write/delete/rename    |
| After successful tests | Read/write inside one specific folder | Full disk access       |
| After trust builds     | Scoped project access                 | Open-ended permissions |
| Mature workflow        | Specific tool actions                 | "Do whatever you need" |

### My Rule

```text
Scope grows with track record.
```

Use Git before letting AI edit files.

---

## Concept 12: Cost, Speed, and Which Model to Use

### Understanding

Different AI tasks have different cost and speed profiles.

General order:

1. Text: cheapest and fastest
2. Speech: still cheap
3. Images: slower and more expensive
4. Video: slowest and most expensive
5. Deep research: slower but useful for complex synthesis

### Key Idea

Iteration cost changes strategy.

For text, iterate freely.

For image/video, invest more in the prompt before generating because each iteration costs more time and money.

### Model Selection

There is no single best AI model. Models are jagged: each is strong at different things.

Useful habit:

```text
Try the same important prompt in 2-3 different models.
Compare the answers.
Keep notes on which model performs best for which task.
```

### Suggested Tool Families to Compare

* ChatGPT
* Claude
* Gemini
* DeepSeek
* Meta AI

### My Tool Strategy

For now:

* Use ChatGPT as the main assistant.
* Use Gemini or Claude as comparison tools.
* Use one backup model for cross-checking important outputs.
* Avoid tool-hopping too much.
* Track patterns in `experiments.md`.

### Monthly Ritual

Once per month:

1. Check current model leaderboards or recent comparisons.
2. Pick one task I do often.
3. Run the same prompt in 2-3 models.
4. Record which model performed best.
5. Update my tool preferences.

---

## Concept 13: Models Checking Models

### Understanding

When there is no answer key, one way to improve quality is to make models critique each other.

Different model families have different blind spots. A second model can catch issues the first model missed.

### Single-Model Self-Critique Loop

Use this for normal tasks.

```text
Score your answer from 1-10 using this rubric:
1. Accuracy
2. Clarity
3. Completeness
4. Practical usefulness
5. Missing risks

For each score:
- give a one-sentence justification
- suggest the change that would raise the score most

Then revise your answer.
```

### Multi-Model Review Loop

Use this for high-stakes work.

1. Generate a draft with the primary model.
2. Ask the primary model to score it using a rubric.
3. Revise until the score improves.
4. Send the draft to a second model from a different family.
5. Ask the second model to critique using the same rubric.
6. Bring the critique back to the first model.
7. Ask it to adopt/reject each point with reasons.
8. For very important work, use a third model.
9. Stop when independent models agree the work is strong.

### Important Caveat

Model scores are progress signals, not truth signals.

For high-stakes legal, medical, financial, or personal decisions, human expert review is still required.

### How I Will Apply This

For my learning:

* Use single-model critique for notes and prompts.
* Use cross-model critique for portfolio README files.
* Use a rubric to evaluate project plans.
* Compare model feedback in `experiments.md`.

---

# Final Recap

## The 13 Concepts

1. **Novice vs Power User**
   Brief AI like a smart new colleague.

2. **Pretrained Knowledge**
   AI is strong on common/stable topics and weak on rare/recent/private topics.

3. **Retrieval Modes**
   Pretrained, web search, and deep research serve different jobs.

4. **Context Is the Whole Game**
   The model only sees what is in the current context window.

5. **Reasoning / Think Hard**
   Use deeper reasoning for complex, multi-step decisions.

6. **Sycophancy**
   AI tends to agree. Use neutral framing and rubrics.

7. **Brainstorm-Iterate Loop**
   Load context, ask for options, give feedback, iterate, then expand.

8. **Multimodal AI**
   Use images, audio, screenshots, and files as context.

9. **Small Apps with One Prompt**
   Use Goal/Input/Output to create quick artifacts and prototypes.

10. **Data Analysis with Code Execution**
    Ask AI to write and run code instead of guessing.

11. **Desktop Apps and Permissions**
    Scope permissions carefully. Ask for plans before actions.

12. **Cost, Speed, and Model Choice**
    Text is cheap to iterate. Use multiple models for important tasks.

13. **Models Checking Models**
    Use self-critique and cross-model critique for stronger outputs.

---

# My Prompt Engineering Operating System

Before every important prompt, I will check:

## 1. Context

Have I provided enough information?

* goal
* background
* constraints
* files
* audience
* output format

## 2. Retrieval Mode

Does this need:

* pretrained knowledge?
* web search?
* deep research?
* uploaded files?
* code execution?

## 3. Framing

Am I biasing the model?

Avoid:

* confirm
* prove
* defend
* support

Use:

* evaluate
* compare
* critique
* score
* find assumptions

## 4. Iteration

Am I asking for the final answer too early?

Better sequence:

```text
options → feedback → revised options → outline → critique → expand → grade → improve
```

## 5. Verification

Do I need:

* citations?
* code execution?
* source quotes?
* cross-model review?
* human expert review?

---

# Personal Application to My Learning Path

I am using this course as part of my Agent Factory learning track.

My goal is not only to read. My goal is to turn each concept into artifacts:

* notes
* prompt templates
* experiments
* small tools
* deployable prototypes

For this course, my main artifact will be:

```text
Prompt Practice Coach
```

The idea:

* The system gives me a scenario.
* I write a prompt.
* The model scores my prompt.
* It identifies missing context, weak framing, lack of constraints, and missing verification.
* It suggests a stronger version.
* I learn prompting patterns through repeated practice.

This helps me build skill through active recall, Feynman-style explanation, feedback, and iteration.