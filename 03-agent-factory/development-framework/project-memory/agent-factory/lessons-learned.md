# Lessons Learned

Reusable lessons from past work on the Agent Factory.

---

## 1. Do not overclaim external side effects
- **Where learned:** Artifact 04 / 05.
- **Why it matters:** Claiming something works without live evidence leads to false confidence and hidden bugs.
- **How to apply later:** Always require evidence logs (Artifact 05 style) before claiming an integration is "done."

## 2. Separate runtime ownership from evidence ownership
- **Where learned:** Artifact 04 vs Artifact 05.
- **Why it matters:** Prevents cluttering the runtime code with complex test harnesses or hardcoded test repos.
- **How to apply later:** Build the adapter in one artifact, prove it in another.

## 3. Fake/default first keeps tests safe and deterministic
- **Where learned:** Artifact 02.
- **Why it matters:** Hitting live APIs during fast dev loops causes rate limits, unwanted side effects, and non-deterministic test failures.
- **How to apply later:** Every tool must have a fake/mock mode that returns standard data.

## 4. Operator approval surface needs vertical workflows
- **Where learned:** Artifact 06.
- **Why it matters:** The workbench is cool, but hard to evaluate in a vacuum without a real agent proposing useful actions.
- **How to apply later:** Move to Phase 03 vertical agents quickly to validate the workbench UX.

## 5. Manual real-mode walkthroughs are learning addenda
- **Where learned:** Artifact 04.
- **Why it matters:** Not every manual test needs to be a formal numbered artifact. Some are just evidence packages.
- **How to apply later:** Use the AFDF evidence protocols to attach proof to existing artifacts instead of creating new ones.

## 6. A reusable session framework reduces context drift
- **Where learned:** Early Phase 02.
- **Why it matters:** Restarting ChatGPT or IDE agent sessions meant losing all architectural context, leading to repeated mistakes.
- **How to apply later:** Always use AFDF bootstraps.

## 7. LLM usage should be a service boundary
- **Where learned:** Foundation design.
- **Why it matters:** Mixing LLM API calls with business logic makes testing hard and violates the "LLM proposes" safety rule.
- **How to apply later:** Isolate LLM calls behind a strict interface; treat their output as untrusted user input.
