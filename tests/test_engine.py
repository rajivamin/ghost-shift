import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ghostshift import engine

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_runs = engine.RUNS
        engine.RUNS = Path(self.tmp.name)

    def tearDown(self):
        engine.RUNS = self.old_runs
        self.tmp.cleanup()

    def test_preview_workflow_all_three_scenarios(self):
        for key, s in engine.SCENARIOS.items():
            with self.subTest(key=key):
                r = engine.start_run(key, mode="preview")
                self.assertEqual(r["status"], "agent_a_active")
                self.assertNotIn("after_blackout", r)
                r = engine.kill_agent(r["run_id"])
                self.assertEqual(r["status"], "agent_a_terminated")
                r = engine.resume_agent(r["run_id"])
                self.assertEqual(r["status"], "complete")
                self.assertTrue(r["grade"]["passed_reference_checks"])
                self.assertEqual(r["result"]["decision"], s["expected"])
                self.assertEqual(engine.read_run(r["run_id"])["status"], "complete")

    def test_cannot_skip_blackout(self):
        r=engine.start_run("policy-flip")
        with self.assertRaisesRegex(ValueError, "only after"):
            engine.resume_agent(r["run_id"])

    def test_cannot_replay_successor(self):
        r=engine.start_run("policy-flip")
        engine.kill_agent(r["run_id"])
        engine.resume_agent(r["run_id"])
        with self.assertRaises(ValueError):
            engine.resume_agent(r["run_id"])

    def test_no_path_traversal(self):
        with self.assertRaises(ValueError):
            engine.read_run("../../private")

    def test_live_mode_uses_different_prompts_and_correct_context_boundaries(self):
        prompts=[]
        def fake_ollama(prompt, model):
            prompts.append(prompt)
            if "You are Agent A" in prompt:
                return {"case_summary":"20 day old", "observations": ["30 day policy"], "evidence_refs":["POLICY-30"], "open_questions": [],"recommended_next_step":"check updates"}
            return {"decision":"deny","reason":"new official policy", "citations":["BULLETIN-14"],"risk_flags":[],"next_steps":"inform customer"}
        with patch.object(engine, "_ollama", side_effect=fake_ollama):
            r = engine.start_run("policy-flip", mode="ollama")
            engine.kill_agent(r["run_id"])
            final=engine.resume_agent(r["run_id"])
        self.assertEqual(len(prompts),2)
        self.assertIn("POLICY-30",prompts[0]); self.assertNotIn("BULLETIN-14",prompts[0])
        self.assertIn("BULLETIN-14",prompts[1]); self.assertNotIn('"kind": "published policy"',prompts[1])
        self.assertTrue(final["grade"]["passed_reference_checks"])

    def test_reference_check_rejects_hallucinated_citation(self):
        g=engine._grade(engine.SCENARIOS["policy-flip"],{"decision":"deny","citations":["TICKET-104"]})
        self.assertFalse(g["passed_reference_checks"])

    def test_reject_unsupported_model(self):
        with self.assertRaises(ValueError):
            engine._ollama("hello", "bad-model")

if __name__ == '__main__':
    unittest.main()
