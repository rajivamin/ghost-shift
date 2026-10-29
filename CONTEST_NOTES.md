# DEV Hacktoberfest 2026 · Contest submission notes

**Ghost Shift** is separate from Multa Lumina. The project was started October 29, 2026, inside the October 26–31 challenge window.

## Rules we need to satisfy

- New repository created within the challenge window.
- A working project with open-source AI at its core. **For the contest, run the Ollama mode and record a real outcome.** Scripted preview alone is not sufficient.
- Working demo: record a short screen walkthrough, or deploy a genuine functional live app. A local video is easiest, and does not require hosting or payment.
- Public code repository link.
- DEV submission based on the official [Submission Template](https://dev.to/challenges/hacktoberfest-week4-2026-10-26), with tags `#devchallenge` and `#hf26challenge`.
- Explain how open-source AI is actually used and why it matters.
- Submit by October 31, 2026, 11:59 PM Pacific; do not assume a grace period.

## Recommended video (60–90 seconds)

1. Show the Ghost Shift title and select **Live local AI · Ollama**, not scripted preview.
2. Show your installed Ollama model name.
3. Start Agent A; display the handoff it created.
4. Trigger **Kill Agent A**. Explain that the original conversation is not passed forward.
5. Trigger **Wake Agent B**, reveal the new policy bulletin, display the actual AI decision.
6. Read out the reference check and any model failure without overstating its significance.
7. Finish with the source repository URL, and the command to reproduce.

## Record these genuine results before drafting the final article

- Model: [FILL IN]
- Ollama version and OS: [FILL IN]
- Scenario(s) run: [FILL IN]
- Decisions and citation checks: [FILL IN]
- Evidence of model failures, if any: [FILL IN]
- Video or live-demo URL: [FILL IN]
- New public GitHub repository URL: [FILL IN]

AI-assisted implementation and text drafting must be disclosed accurately under DEV's current AI disclosure UI. No partner category should be claimed without meaningful use of its listed technology.


## QA reflection and follow-up

- Four baseline live Gemma runs were completed. See `audit/QA_REFLECTION_ORIGINAL.md` for the initial reflection; retain original run JSON on the developer machine.
- `audit/engine_v0.2_baseline.py` preserves the pre-correction engine.
- v0.3 adds a supplementary QA rubric and structured evidence claims. It is a **new protocol**, not a retroactive improvement of historical model outputs.
- All 17 automated tests passed in the prepared source bundle. `py -3 audit/replay_qa_probe.py` demonstrates two synthetic scorer probes and does **not** call Ollama.
- In the submission clearly separate fictional film, four old live experiments, scorer QA probes, and any new v0.3 model results.
