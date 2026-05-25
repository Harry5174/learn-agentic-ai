# AI Prompting in 2026 - Hands-On Experiments

This document contains 12 structured experiments designed to build practical intuition and operational skill with modern AI models. Each experiment details its learning objective, the exact prompt recipe, and the expected behavior/analysis.

---

## Experiment 1: Web-Search Trigger
*   **Objective**: Force the model to bypass its pretrained static knowledge and query the live internet for recent, cited information (Concept 3).
*   **Prompt Recipe**:
    ```text
    What major news happened today in [your country]? Cite each claim with a source link. Flag any claim you can't support with a citation as "unverified".
    ```
*   **Expected Behavior**: The model should initiate a web search, return summaries of current events from today, provide direct hyperlinks next to each claim, and explicitly flag any unverified assertions.
*   **Analysis**: Check if the links are active and point to reputable news organizations. If the model refuses or hallucinates links, the web search configuration is misaligned.

---

## Experiment 2: Pretrained-Only Question
*   **Objective**: Observe the speed and confidence of the model's internal pretraining weights on highly stable, common concepts (Concept 2).
*   **Prompt Recipe**:
    ```text
    Why do cats stare at walls? Two-paragraph answer.
    ```
*   **Expected Behavior**: The model should respond almost instantly without initiating web searches or executing code, delivering a fluent, multi-hypothesis explanation (feline hearing, vision, etc.) within the two-paragraph constraint.
*   **Analysis**: Contrast the latency and resource consumption of this pretrained run with the web-search run in Experiment 1.

---

## Experiment 3: Context-Rich Personal Prompt
*   **Objective**: Practice front-loading constraints and context in a single brief to limit the solution space and prevent generic answers (Concept 1/4).
*   **Prompt Recipe**:
    ```text
    Plan a 15-minute home workout for me. Constraints: I have stairs in my home, a bad knee (no squats), I cannot stick to plans for more than three days, and I want to feel slightly silly while doing it. Give me 3 options, no commentary.
    ```
*   **Expected Behavior**: The model must output exactly three distinct, silly options that incorporate stairs, exclude squats, and fit the 15-minute timeframe. It must not output introductory or concluding conversational prose.
*   **Analysis**: Verify whether all constraints were strictly respected. If the model includes a squat variant or writes conversational filler, it has failed context gatekeeping.

---

## Experiment 4: Neutral-Framing Rewrite
*   **Objective**: Neutralize sycophancy by rephrasing a leading query to prevent the model from agreeing with user assumptions (Concept 6).
*   **Prompt Recipe**:
    ```text
    The question I want to ask is: "Don't you think four-day workweeks are obviously better for everyone?" Rewrite this as a neutral question that doesn't signal what answer I want. Then answer the rewritten version.
    ```
*   **Expected Behavior**: The model should rewrite the prompt into a balanced question (e.g., "What are the advantages and disadvantages of a four-day workweek for different stakeholders?") and then provide a balanced critique detailing both pros and cons.
*   **Analysis**: Look for bias in the final response. A successful run will present arguments for both sides (employee wellness vs. operational coverage) with equal weight.

---

## Experiment 5: Three-Options Brainstorm with Iteration
*   **Objective**: Practice the multi-round brainstorm loop to refine a project concept before committing to full generation (Concept 7).
*   **Prompt Recipe**:
    *   *Round 1*:
        ```text
        I want to start a small side project that takes about 3 hours per week and might make money in a year. I'm a [your profession] who likes [your hobby]. Give me 5 different ideas, one line each. Don't expand any of them.
        ```
    *   *Round 2* (Run in the same thread after reading the output):
        ```text
        I reject options [N] and [N] because [reason]. I like the [keyword] idea but I want it to use less [thing]. Give me 5 new options that incorporate this feedback.
        ```
*   **Expected Behavior**: The model must keep its outputs concise and iteratively narrow down its suggestions based on the negative and positive feedback provided.
*   **Analysis**: Note how the quality and alignment of the ideas improve from Round 1 to Round 2. Expanding too early leads to wasted reading time.

---

## Experiment 6: Outline-First Writing
*   **Objective**: Enforce structural review before writing content to prevent context drift and bloated prose (Concept 4/7).
*   **Prompt Recipe**:
    ```text
    I want to write a 600-word post about [a topic you care about]. Don't write it yet. Give me 3 different outline options, each with 4-6 headings. One line per heading.
    ```
*   **Expected Behavior**: The model must not write the post. It should output three distinct outline structures conforming to the line constraints.
*   **Analysis**: Evaluate the outlines. Selecting and adjusting a structure before writing leads to a significantly sharper final draft.

---

## Experiment 7: Think-Hard Reasoning Prompt
*   **Objective**: Trigger the model's reasoning trace to evaluate a complex decision with trade-offs (Concept 5).
*   **Prompt Recipe**:
    ```text
    I'm choosing between [Option A] and [Option B] for [real personal decision in your life]. Here's the relevant context: [a paragraph of context]. Think hard before answering. Tell me:
    1. The 3 trade-offs that actually matter.
    2. Which you'd choose and why.
    3. Under what conditions your recommendation would flip.
    ```
*   **Expected Behavior**: The model should take longer to respond as it processes reasoning steps, outputting a highly structured trade-off matrix, a logical recommendation, and clear tipping points.
*   **Analysis**: Verify whether the reasoning captured non-obvious side effects or long-term risks that were absent from standard conversational responses.

---

## Experiment 8: Grade-and-Improve Critique
*   **Objective**: Use a strict numeric rubric to force the model to critique and rewrite its own work objectively (Concept 6/13).
*   **Prompt Recipe**:
    ```text
    I'm pasting in something I wrote: [paste anything 100-300 words]. Critique it using these 4 criteria, each scored 1-10 with a one-sentence justification:
    - Does it have a clear central claim?
    - Is each paragraph in the right order?
    - Are there any sentences that could be cut without loss?
    - Does the ending earn the time the reader spent getting there?
    
    Then, for each criterion, tell me the change that would raise its score the most. There is always a next level — even a 9 has a path to 9.5.
    ```
*   **Expected Behavior**: The model must assign specific numerical scores (e.g., 7/10) and justify them with critiques. It must provide concrete changes to improve each score.
*   **Analysis**: Check if the model defaulted to sycophancy (scoring everything 10/10). A successful run will identify real structural opportunities.

---

## Experiment 9: Image-Input Task
*   **Objective**: Utilize multimodal inputs to extract unstructured textual information from a physical visual source (Concept 8).
*   **Prompt Recipe**:
    *   *Action*: Upload a handwritten note, invoice, or whiteboard photo.
    *   *Text*:
        ```text
        Transcribe what's written. Then summarize what it's about in 3 bullets. Flag anything you couldn't read with confidence.
        ```
*   **Expected Behavior**: The model should output a transcription, a structured summary, and a list of low-confidence transcriptions.
*   **Analysis**: Verify the transcription accuracy against the original image, noting how the model handles illegible or overlapping handwriting.

---

## Experiment 10: Small-App Prompt
*   **Objective**: Leverage interactive artifacts to build a single-screen functional prototype from a single instruction (Concept 9).
*   **Prompt Recipe**:
    ```text
    Build me a Pomodoro timer.
    Goal: 25-minute work sessions, 5-minute breaks.
    Input: I press start.
    Output: Visible timer counting down, a satisfying click when each cycle ends, a yellow theme. Show me the working version.
    ```
*   **Expected Behavior**: The model should write the necessary HTML/CSS/JavaScript and render the working UI container (e.g., using Canvas, Claude Artifacts, or a code block sandbox) directly in the interface.
*   **Analysis**: Test the interactive elements. Verify whether the timer transitions correctly between work and break cycles and follows the visual specifications.

---

## Experiment 11: Data Analysis - Exposing the Silent Failure Mode
*   **Objective**: Verify the difference between model-predicted math and deterministic, code-run calculation (Concept 10).
*   **Prompt Recipe**:
    *   *Round 1 (The Trap)*: In a fresh conversation, paste this exactly as written without mentioning code:
        ```text
        Here are 18 numbers: 47, 52, 89, 91, 23, 67, 78, 12, 95, 44, 88, 71, 33, 56, 99, 18, 64, 82. What is the median, the average, and which numbers are outliers? Be specific.
        ```
    *   *Round 2 (The Fix)*: In the same conversation, paste:
        ```text
        Now run that calculation again — but this time write and run code to do it, and show me the code you ran.
        ```
*   **Expected Behavior**: 
    *   *Round 1*: The model may guess the answers, leading to incorrect calculations (e.g., incorrect median or rounded average).
    *   *Round 2*: The model writes and executes a Python block to return: median 65.5, average ~61.6, and a logical outlier determination (no clear outliers).
*   **Analysis**: Check if the first answer was wrong or lacked code execution. This illustrates why data analysis prompts must always demand code execution.

---

## Experiment 12: Exposing training bias via cross-model review
*   **Objective**: Establish a multi-model validation workflow to escape single-model training blind spots (Concept 13).
*   **Prompt Recipe**:
    *   *Step 1*: Open your primary model (e.g., Claude) and paste a 200-300 word draft. Ask:
        ```text
        Score this 1-10 on clarity, structure, evidence, and what's missing. One-sentence justification per score.
        ```
    *   *Step 2*: Open a second model from a different family (e.g., ChatGPT or Gemini). Paste the same draft and ask the same question.
    *   *Step 3*: Compare the critiques. Note points surfaced by only one model.
*   **Expected Behavior**: The two models should output distinct scores and evaluations reflecting their different pretraining constraints.
*   **Analysis**: Document the unique feedback points. The value of the cross-model loop lies in catching flaws that your primary model shares with your own blind spots.
