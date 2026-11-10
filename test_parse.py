"""Parser tests. SYNTHETIC fixture: replace/add real output from your ADMIXTOOLS version."""
from qpadm_pipeline.parse import classify_model, parse_qpadm_output

FIXTURE = """
numsnps used: 500000
f4rank: 0 dof: 6 chisq: 40.1 tail: 1.0e-06 dofdiff: 0 chisqdiff: 0 taildiff: 1
f4rank: 1 dof: 3 chisq: 3.2 tail: 0.3622 dofdiff: 3 chisqdiff: 36.9 taildiff: 4.8e-08
best coefficients: 0.600 0.400
std. errors: 0.050 0.050
"""


def test_parses_synthetic_output():
    r = parse_qpadm_output(FIXTURE)
    assert r["coefficients"] == [0.6, 0.4]
    assert r["std_errors"] == [0.05, 0.05]
    assert r["p_value"] == 0.3622
    assert r["n_snps"] == 500000
    assert r["warnings"] == []


def test_missing_fields_are_reported_not_guessed():
    r = parse_qpadm_output("nothing useful here")
    assert r["p_value"] is None
    assert r["warnings"]


def test_classification():
    assert classify_model([0.6, 0.4], 0.36) == "not_rejected"
    assert classify_model([0.6, 0.4], 0.01) == "rejected"
    assert classify_model([1.2, -0.2], 0.36) == "infeasible_coefficients"
    assert classify_model(None, None) == "unknown"
