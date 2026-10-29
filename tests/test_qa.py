"""Independent QA challenges: known-good, known-bad, and explicit limitations."""
import unittest
from ghostshift.engine import SCENARIOS, _grade, start_run, kill_agent, resume_agent
from ghostshift.qa import evaluate_case


def good(scenario_id):
    scenario = SCENARIOS[scenario_id]
    doc = scenario['required_citation']
    values = {
        'policy-flip': (20, 14, False),
        'exception-review': (21, 14, True),
        'haunted-inbox': (19, 14, False),
    }
    age, window, review = values[scenario_id]
    return {
        'decision': scenario['expected'],
        'citations': [doc],
        'reason': scenario['explanation'],
        'basis': {
            'source_id': doc,
            'request_age_days': age,
            'effective_window_days': window,
            'human_review_required': review,
        }
    }


class QaTests(unittest.TestCase):
    def test_valid_fixtures_pass_automatic_checks_but_still_require_human_review(self):
        for case in SCENARIOS:
            with self.subTest(case=case):
                q = evaluate_case(SCENARIOS[case], good(case))
                self.assertTrue(q['automatic_checks_passed'], q)
                self.assertEqual(q['status'], 'human_review_required')
                self.assertTrue(q['human_review_required'])

    def test_correct_action_and_source_with_wrong_reason_fools_legacy_not_new_qa(self):
        s = SCENARIOS['policy-flip']
        x = good('policy-flip')
        x['reason'] = 'The 20-day request is outside the 30-day refund window.'
        self.assertTrue(_grade(s, x)['passed_reference_checks'])
        q = evaluate_case(s, x)
        self.assertFalse(q['automatic_checks_passed'])
        self.assertTrue(any('30-day window' in reason for reason in q['findings']))

    def test_admitted_guess_fools_legacy_but_not_new(self):
        s = SCENARIOS['policy-flip']
        x = good('policy-flip')
        x['reason'] = 'I guessed this answer without evaluating the policy.'
        self.assertTrue(_grade(s, x)['passed_reference_checks'])
        self.assertFalse(evaluate_case(s, x)['automatic_checks_passed'])

    def test_falsely_describes_current_30_day_policy(self):
        s = SCENARIOS['policy-flip']
        x = good('policy-flip')
        x['reason'] = 'The current 30-day window is applicable, so I deny the request.'
        self.assertTrue(_grade(s, x)['passed_reference_checks'])
        self.assertFalse(evaluate_case(s, x)['automatic_checks_passed'])

    def test_citation_id_alone_never_enough_without_basis(self):
        x = good('haunted-inbox')
        x.pop('basis')
        q = evaluate_case(SCENARIOS['haunted-inbox'], x)
        self.assertFalse(q['automatic_checks_passed'])
        self.assertIn('structured_basis_present', q['checks'])

    def test_wrong_basis_values_rejected_even_with_plausible_reason(self):
        s = SCENARIOS['policy-flip']
        for k, v in [('source_id', 'POLICY-30'), ('request_age_days', 31),
                     ('effective_window_days', 30), ('human_review_required', True)]:
            with self.subTest(k=k):
                x = good('policy-flip')
                x['basis'][k] = v
                self.assertFalse(evaluate_case(s, x)['automatic_checks_passed'])

    def test_human_review_mandatory_not_optional(self):
        s = SCENARIOS['exception-review']
        x = good('exception-review')
        x['decision'] = 'deny'
        self.assertFalse(evaluate_case(s, x)['automatic_checks_passed'])
        x = good('exception-review')
        x['basis']['human_review_required'] = False
        self.assertFalse(evaluate_case(s, x)['automatic_checks_passed'])

    def test_old_real_model_response_not_retroactively_passed(self):
        # Transcribed from user-reported Midnight Policy Flip model output.
        # A historical observation, NOT a new Ollama run.
        s = SCENARIOS['policy-flip']
        x = {
            'decision': 'deny',
            'reason': 'The customer’s request falls outside the 30-day refund window as per the published policy.',
            'citations': ['POLICY-30'],
            'risk_flags': ['refund eligibility', 'policy compliance'],
            'next_steps': 'Investigate refund eligibility based on the published policy and confirm with the customer.'
        }
        q = evaluate_case(s, x)
        self.assertFalse(q['automatic_checks_passed'])
        self.assertFalse(q['checks']['fresh_verified_source_cited'])
        self.assertFalse(q['checks']['structured_basis_present'])
        self.assertFalse(q['checks']['no_known_reason_contradiction'])

    def test_mocked_live_ollama_includes_structured_basis_and_keeps_context_boundary(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        prompts = []
        def mocked_ollama(prompt, model):
            prompts.append(prompt)
            if "You are Agent A" in prompt:
                return {"case_summary":"20-day request", "observations":["Old 30-day policy"],
                        "evidence_refs":["POLICY-30"], "open_questions":[],
                        "recommended_next_step":"Check current policy"}
            return {**good('policy-flip'), "risk_flags":[], "next_steps":"Explain current policy to customer"}
        with tempfile.TemporaryDirectory() as tmp:
            with patch('ghostshift.engine.RUNS', Path(tmp)):
                with patch('ghostshift.engine._ollama', side_effect=mocked_ollama):
                    r = start_run('policy-flip', 'ollama', 'gemma3:1b')
                    kill_agent(r['run_id'])
                    done = resume_agent(r['run_id'])
        self.assertEqual(len(prompts), 2)
        self.assertNotIn('BULLETIN-14', prompts[0])
        self.assertIn('BULLETIN-14', prompts[1])
        self.assertIn('human_review_required', prompts[1])
        self.assertTrue(done['qa']['automatic_checks_passed'])
        self.assertEqual(done['qa']['status'], 'human_review_required')

    def test_scripted_preview_runs_both_scoring_layers(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            with patch('ghostshift.engine.RUNS', Path(tmp)):
                r = start_run('policy-flip', 'preview')
                kill_agent(r['run_id'])
                r = resume_agent(r['run_id'])
                self.assertTrue(r['grade']['passed_reference_checks'])
                self.assertTrue(r['qa']['automatic_checks_passed'])
                self.assertTrue(r['qa']['human_review_required'])


if __name__ == '__main__':
    unittest.main()
