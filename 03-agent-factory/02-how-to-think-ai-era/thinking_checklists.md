# Thinking Checklists and Templates

Use these templates and checklists to execute the six thinking disciplines during high-stakes AI sessions.

---

## 1. Prediction Lock Template

Fill out this four-line block before you open any AI interface.

```markdown
### Prediction Lock

1. Real Question: What is this decision or problem actually about beneath the surface?
   [Your response here]

2. Load-Bearing Fact: What is the single most critical fact that would determine the outcome?
   [Your response here]

3. Estimated Answer: What is your guess for that fact or outcome? (Must be a specific, testable claim)
   [Your response here]

4. Flip Condition: How confident are you (0-100%), and what specific evidence would cause your estimate to flip?
   [Your response here]
```

---

## 2. Reasoning Receipt Log

Use this format to log load-bearing recommendations during your AI session.

| Item Reference | AI Claim / Recommendation | Status | Justification (The "Why") |
| :--- | :--- | :--- | :--- |
| `01` | [Copy-paste the AI recommendation here] | `[ACCEPT / REJECT / MODIFY / SURFACED / MISSED]` | [Explain your choice using local constraints or facts] |
| `02` | [Copy-paste the AI recommendation here] | `[ACCEPT / REJECT / MODIFY / SURFACED / MISSED]` | [Explain your choice using local constraints or facts] |
| `03` | [Copy-paste the AI recommendation here] | `[ACCEPT / REJECT / MODIFY / SURFACED / MISSED]` | [Explain your choice using local constraints or facts] |

---

## 3. Error Taxonomy Scanning Sheet

Do not read the AI response for overall flow. Instead, run six separate scans, searching for one category of error at a time.

```markdown
### Error Scan

- [ ] Scan 1: Factual Errors
  - Action: Check every number, date, name, calculation, and API method.
  - Flagged: [Quote the text and note the error, or write "Checked, nothing found"]

- [ ] Scan 2: Logical Gaps
  - Action: Check if conclusions follow logically from the premises. Look for "therefore," "thus," and "as a result."
  - Flagged: [Quote the text and note the gap, or write "Checked, nothing found"]

- [ ] Scan 3: False Confidence
  - Action: Look for authoritative assertions on contested topics. Check if the model omitted hedging words like "typically" or "potentially."
  - Flagged: [Quote the text and note the false confidence, or write "Checked, nothing found"]

- [ ] Scan 4: Missing Context
  - Action: Identify local constraints, target audiences, or operational limitations that the model ignored.
  - Flagged: [Quote the text and note what was missed, or write "Checked, nothing found"]

- [ ] Scan 5: Fabricated Sources
  - Action: Verify citations, URLs, book references, and external library methods.
  - Flagged: [Quote the text and note the fabrication, or write "Checked, nothing found"]

- [ ] Scan 6: Stale Facts
  - Action: Check for deprecated software libraries, outdated pricing, or changes in industry regulations.
  - Flagged: [Quote the text and note the stale fact, or write "Checked, nothing found"]
```

---

## 4. Cascade Map Builder

Map the consequences of a decision three layers deep across five stakeholder domains.

```markdown
### Cascade Map

Decision Statement: [Write your decision in one clear sentence]

Stakeholder Domain 1: [e.g., Development Team]
- Layer 1 (Immediate Effect): [Effect]
- Layer 2 (Secondary Effect): [Effect]
- Layer 3 (Tertiary Effect): [Effect]

Stakeholder Domain 2: [e.g., End Users]
- Layer 1 (Immediate Effect): [Effect]
- Layer 2 (Secondary Effect): [Effect]
- Layer 3 (Tertiary Effect): [Effect]

Stakeholder Domain 3: [e.g., System Latency/Infrastructure]
- Layer 1 (Immediate Effect): [Effect]
- Layer 2 (Secondary Effect): [Effect]
- Layer 3 (Tertiary Effect): [Effect]

Stakeholder Domain 4: [e.g., Compliance/Security]
- Layer 1 (Immediate Effect): [Effect]
- Layer 2 (Secondary Effect): [Effect]
- Layer 3 (Tertiary Effect): [Effect]

Stakeholder Domain 5: [e.g., Long-term Maintenance]
- Layer 1 (Immediate Effect): [Effect]
- Layer 2 (Secondary Effect): [Effect]
- Layer 3 (Tertiary Effect): [Effect]

Feedback Loop Identification:
- Trace how a Layer 3 effect from one domain circles back to impact the initial Decision Statement or another domain.
- Loop Description: [e.g., Tertiary Effect X in Infrastructure increases operational cost, which cancels out the cost savings of Decision Statement Y]
```

---

## 5. First Principles Threshold Table

Define the specific boundaries where general consensus advice fails.

| General Recommendation / Rule of Thumb | Named Threshold (Specific Conditions/Numbers) | Override Action / Alternative Strategy |
| :--- | :--- | :--- |
| [e.g., Use microservices to scale applications] | When team size is under 5 developers AND service-to-service communication latency exceeds 50ms | Use a monolithic architecture with strict modular packaging instead |
| [e.g., Write comprehensive unit tests for all paths] | When code is a disposable prototype with a lifecycle under 3 weeks AND user base is under 50 testers | Rely on automated integration smoke tests and manual verification loops |
| [e.g., Add caching to database queries] | When query execution time is under 10ms AND database CPU utilization is under 20% | Maintain direct queries to avoid cache invalidation complexity |

---

## 6. Three-Path Override Log

Log the outputs of your three paths and document your unique value add.

```markdown
### Three-Path Comparison

1. Solo Draft Key Ideas (15 min brainstorm, no AI):
   - [Core point 1]
   - [Core point 2]

2. AI-Only Draft Key Ideas (5 min prompt, no manual editing):
   - [AI consensus point 1]
   - [AI consensus point 2]

3. Collaborative Draft Overrides (10 min synthesis):
   - Override 1: [Quote what you changed or added, and explain how it improved the draft]
   - Override 2: [Quote what you changed or added, and explain how it improved the draft]
   - Override 3: [Quote what you changed or added, and explain how it improved the draft]
```
