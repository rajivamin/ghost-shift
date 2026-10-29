# Ghost Shift QA update: evidence and reproducibility

**Sequence matters.** The first four `gemma3:1b` runs were completed under the original v0.2 prompts/scorer on the creator's Windows Ollama installation. Their JSON files stay in the creator's existing `runs/` directory and are not included in this distribution. Those results are described in `QA_REFLECTION_ORIGINAL.md` from the creator's screenshots and copied outputs. No results were retroactively changed.

## Baseline preservation

- `audit/engine_v0.2_baseline.py` retains the original engine used to establish the limitations. It is not imported by the live app.
- The original `_grade` scorer still runs in `ghostshift/engine.py` to produce a visible historical comparison.
- The additional `ghostshift/qa.py` scorer and new `basis` response schema define a **new experiment protocol**. A new run is not directly comparable to the original four as if everything except the scorer stayed fixed.

## New checks (closed-world, experimental)

1. Required decision for the frozen scenario.
2. Citation of the verified source delivered after the blackout (source kind independently checked against the scenario fixture).
3. Structured `basis` fields for source ID, request age, effective window, and human-review requirement. Missing data fail the automated rubric.
4. A few explicitly known contradictory explanation patterns, including claiming a 20-day request is outside a 30-day policy.
5. Human approval is never substituted by the model's judgment in the test's intended rubric. There are no actual business actions in Ghost Shift.

These checks **do not** prove that model explanations are true in general; the model can fabricate its structured basis; regular expressions cannot verify arbitrary reasoning. Even a clean automatic result is marked `human_review_required` and must not be treated as organizational authorization.

## Reproduce the QA comparison (NO model inference)

From the project root:

```powershell
py -3 audit/replay_qa_probe.py
py -3 -m unittest discover -s tests -v
```

The replay demonstrates that the original scorer accepts a contrived contradiction with the correct action and required citation while the added QA layer rejects it. A sound closed-world example clears automatic checks but still requires human review.

## New real local-model rerun (separate observation)

1. Stop the running v0.2 web server with Ctrl+C. Preserve the original `runs/` files.
2. Install/copy the v0.3 patch; restart `py -3 -m ghostshift.web` in the same project folder.
3. Select `The midnight policy flip`, `Live local AI · Ollama`, `gemma3:1b`.
4. Start Agent A, terminate Agent A, and wake Agent B.
5. Save the **new** run's JSON and report both the original baseline score and the added QA outcome, including the `basis` object and any findings.
6. Disclose Ollama/model/version and whether the model returned the new schema. Never label scripted preview or mocked tests as real AI results.

## Not yet independently validated

- The three scenario rules are developer-defined, not externally adjudicated.
- The new scorer itself needs further adversarial testing (including overzealous contradiction matching, semantic paraphrases, and incomplete evidence).
- There is no blinded held-out evaluation set, external model-replication study, operational safety certification, or real refund tool.
- No external organization has approved this QA rubric.
