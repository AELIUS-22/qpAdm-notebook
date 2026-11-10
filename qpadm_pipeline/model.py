"""Model specification, execution, and ledger entry for one qpAdm model."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .parse import classify_model, parse_qpadm_output
from .prepare import write_parfile
from .runner import Workspace, append_ledger, make_run_id, run_command, sha256_file


@dataclass
class ModelSpec:
    target: str
    sources: list
    right: list
    allsnps: bool = True
    phase: str = "exploratory"  # benchmark / sensitivity / exploratory

    @classmethod
    def from_json(cls, path) -> "ModelSpec":
        data = json.loads(Path(path).read_text())
        data = {k: v for k, v in data.items() if not k.startswith("_")}
        return cls(target=data["target"], sources=data["sources"], right=data["right"],
                   allsnps=data.get("allsnps", True), phase=data.get("phase", "exploratory"))

    def validate(self) -> None:
        if len(self.sources) < 2:
            raise ValueError("qpAdm needs at least two source populations.")
        left = [self.target] + list(self.sources)
        if len(set(left)) != len(left):
            raise ValueError("Duplicate populations in target/sources.")
        overlap = set(left) & set(self.right)
        if overlap:
            raise ValueError(f"Populations in both left and right sets: {sorted(overlap)}")


def run_model(ws: Workspace, spec: ModelSpec, merged_prefix, hash_genotypes: bool = False) -> dict:
    spec.validate()
    merged_prefix = Path(str(merged_prefix))
    hashes = {ext: sha256_file(Path(str(merged_prefix) + ext)) for ext in (".snp", ".ind")}
    if hash_genotypes:  # slow for large AADR-sized files
        hashes[".geno"] = sha256_file(Path(str(merged_prefix) + ".geno"))

    manifest = {"target": spec.target, "sources": spec.sources, "right": spec.right,
                "allsnps": spec.allsnps, "phase": spec.phase, "dataset_hashes": hashes}
    run_id = make_run_id(json.dumps(manifest, sort_keys=True))

    model_dir = ws.root / "models" / run_id
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "left.txt").write_text("\n".join([spec.target] + spec.sources) + "\n")
    (model_dir / "right.txt").write_text("\n".join(spec.right) + "\n")
    (model_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    par = write_parfile(model_dir / "qpadm.par", {
        "genotypename": f"{merged_prefix}.geno",
        "snpname": f"{merged_prefix}.snp",
        "indivname": f"{merged_prefix}.ind",
        "popleft": model_dir / "left.txt",
        "popright": model_dir / "right.txt",
        "details": "YES",
        "allsnps": "YES" if spec.allsnps else "NO",
    })

    record, stdout = run_command(ws, [ws.qpadm, "-p", par], "qpadm", run_id,
                                 extra={"manifest": manifest}, check=False)

    result = {"type": "result", "run_id": run_id, "phase": spec.phase, "target": spec.target,
              "sources": spec.sources, "right": spec.right,
              "runtime_seconds": record["runtime_seconds"], "command_status": record["status"]}
    if record["status"] != "ok":
        result.update(status="failed", model_status="unknown", coefficients=None,
                      std_errors=None, p_value=None, n_snps=None,
                      warnings=["qpAdm run failed; see logs."])
    else:
        parsed = parse_qpadm_output(stdout)
        status = "ok" if not parsed["warnings"] else "parse_incomplete"
        result.update(parsed)
        result.update(status=status,
                      model_status=classify_model(parsed["coefficients"], parsed["p_value"]))
    append_ledger(ws, result)  # rejected and failed models are kept too
    return result
