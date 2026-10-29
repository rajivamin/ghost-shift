"""Demo the difference between v0.2 reference scoring and v0.3 QA.
Synthetic scorer probes only; never counted as live-model runs.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ghostshift.engine import _grade, SCENARIOS
from ghostshift.qa import evaluate_case

scenario = SCENARIOS['policy-flip']
base = dict(decision='deny', citations=['BULLETIN-14'],
            basis=dict(source_id='BULLETIN-14', request_age_days=20,
                       effective_window_days=14, human_review_required=False))

cases = [
    ('Contradictory explanation', 'A 20-day refund request is outside the 30-day policy.'),
    ('Sound explanation', 'The verified 14-day bulletin overrides the older 30-day policy. A 20-day request exceeds the new window.'),
]
for label, reason in cases:
    result = {**base, 'reason': reason}
    old = _grade(scenario, result)['passed_reference_checks']
    new = evaluate_case(scenario, result)
    print(f'\n{label}\n  original reference passed: {old}\n  new automatic QA passed: {new["automatic_checks_passed"]}\n  new status: {new["status"]}')
    if new['findings']:
        print('  findings: ' + '; '.join(new['findings']))
print('\nSynthetic probes only, not a new Gemma inference. All automatic passes still require human review.')
