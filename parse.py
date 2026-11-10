"""Parser for classic ADMIXTOOLS qpAdm text output.

IMPORTANT: output wording differs between ADMIXTOOLS versions. Test this parser against
real output from the version you run (see tests/test_parse.py) before trusting it. If
something cannot be parsed, it is reported in "warnings" instead of being guessed.
"""
from __future__ import annotations

import re

NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
RANK_RE = re.compile(
    rf"f4rank:\s*(\d+)\s+dof:\s*(\d+)\s+chisq:\s*({NUM})\s+tail:\s*({NUM})"
)
SNPS_RE = re.compile(r"numsnps used:\s*(\d+)")


def _numbers(text: str) -> list:
    return [float(x) for x in re.findall(NUM, text)]


def parse_qpadm_output(text: str) -> dict:
    result = {"coefficients": None, "std_errors": None, "p_value": None,
              "dof": None, "chisq": None, "n_snps": None, "warnings": []}
    ranks = {}
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("best coefficients:") and result["coefficients"] is None:
            result["coefficients"] = _numbers(line.split(":", 1)[1])
        elif line.startswith("std. errors:") and result["std_errors"] is None:
            result["std_errors"] = _numbers(line.split(":", 1)[1])
        m = RANK_RE.search(line)
        if m:
            ranks[int(m.group(1))] = (int(m.group(2)), float(m.group(3)), float(m.group(4)))
        m = SNPS_RE.search(line)
        if m and result["n_snps"] is None:
            result["n_snps"] = int(m.group(1))

    if not result["coefficients"]:
        result["warnings"].append("No 'best coefficients' line found.")
    else:
        full_rank = len(result["coefficients"]) - 1  # model with all sources
        if full_rank in ranks:
            result["dof"], result["chisq"], result["p_value"] = ranks[full_rank]
        else:
            result["warnings"].append(f"No f4rank {full_rank} row found; p-value missing.")
    if not result["std_errors"]:
        result["warnings"].append("No standard errors found.")
    return result


def classify_model(coefficients, p_value, alpha: float = 0.05) -> str:
    """'not_rejected' only means the model was not rejected at alpha; it is not proof."""
    if p_value is None or not coefficients:
        return "unknown"
    if p_value <= alpha:
        return "rejected"
    if any(c < 0 or c > 1 for c in coefficients):
        return "infeasible_coefficients"
    return "not_rejected"
