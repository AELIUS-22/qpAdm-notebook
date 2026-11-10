"""Command-line interface: prepare -> run -> report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model import ModelSpec, run_model
from .plot import plot_results
from .prepare import prepare_inputs
from .runner import PipelineError, Workspace


def load_results(ledger: Path) -> list:
    rows = []
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("type") == "result":
                    rows.append(rec)
    return rows


def main(argv=None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--workdir", default="work")
    common.add_argument("--plink", default="plink")
    common.add_argument("--convertf", default="convertf")
    common.add_argument("--mergeit", default="mergeit")
    common.add_argument("--qpadm", default="qpAdm")

    parser = argparse.ArgumentParser(prog="qpadm_pipeline", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", parents=[common], help="raw file -> merged AADR dataset")
    p.add_argument("--raw", required=True, help="23andMe-format raw data file")
    p.add_argument("--sample-id", default="MySample")
    p.add_argument("--reference-prefix", required=True,
                   help="AADR EIGENSTRAT prefix (without .geno/.snp/.ind)")

    r = sub.add_parser("run", parents=[common], help="run one qpAdm model")
    r.add_argument("--config", required=True, help="model JSON (see examples/)")
    r.add_argument("--merged-prefix", help="default: <workdir>/merged/merged")
    r.add_argument("--hash-genotypes", action="store_true")

    s = sub.add_parser("report", parents=[common], help="print all results and plot")
    s.add_argument("--out", default="ancestry_plot.png")

    a = parser.parse_args(argv)
    ws = Workspace(Path(a.workdir), plink=a.plink, convertf=a.convertf,
                   mergeit=a.mergeit, qpadm=a.qpadm)
    try:
        if a.cmd == "prepare":
            merged = prepare_inputs(ws, a.raw, a.sample_id, a.reference_prefix)
            print(f"Merged dataset: {merged}\nSNP counts: {ws.root / 'qc_report.json'}")
        elif a.cmd == "run":
            merged = a.merged_prefix or ws.root / "merged" / "merged"
            res = run_model(ws, ModelSpec.from_json(a.config), merged, a.hash_genotypes)
            print(f"run {res['run_id']}: {res['status']} / {res['model_status']} "
                  f"p={res.get('p_value')} coefficients={res.get('coefficients')}")
        else:
            rows = load_results(ws.ledger)
            for x in rows:  # every run is listed, including rejected and failed ones
                print(x["run_id"], x["target"], x["status"], x["model_status"],
                      x.get("p_value"), x.get("coefficients"))
            plot_results([x for x in rows if x["status"] == "ok"], a.out)
            print(f"Plot saved to {a.out}")
    except (PipelineError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
