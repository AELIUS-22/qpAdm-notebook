"""Genotype preparation: raw consumer file -> PLINK -> EIGENSTRAT -> merge with AADR.

Reports SNP counts at each stage. It does NOT perform full build/allele/strand
harmonization beyond what PLINK, convertf and mergeit do themselves; inspect the saved
logs for allele warnings.
"""
from __future__ import annotations

import json
from pathlib import Path

from .runner import Workspace, make_run_id, run_command, sha256_file


def _p(prefix, ext: str) -> Path:
    # Don't use with_suffix(): AADR prefixes contain dots (e.g. v62.0_1240k_public).
    return Path(str(prefix) + ext)


def write_parfile(path: Path, params: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{k}: {v}\n" for k, v in params.items()), encoding="utf-8")
    return path


def count_lines(path: Path, skip_comments: bool = False) -> int:
    n = 0
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.strip() and not (skip_comments and line.startswith("#")):
                n += 1
    return n


def set_population_label(ind_path: Path, label: str) -> None:
    """Set the population (3rd column) of every individual in an EIGENSTRAT .ind file."""
    rows = []
    for line in Path(ind_path).read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        while len(parts) < 3:
            parts.append("U")
        parts[2] = label
        rows.append("\t".join(parts[:3]))
    Path(ind_path).write_text("\n".join(rows) + "\n")


def prepare_inputs(ws: Workspace, raw_file, sample_id: str, reference_prefix) -> Path:
    """Run the full preparation. Returns the merged dataset prefix."""
    raw_file, ref = Path(raw_file), Path(str(reference_prefix))
    for ext in (".geno", ".snp", ".ind"):
        if not _p(ref, ext).exists():
            raise FileNotFoundError(f"Reference file missing: {_p(ref, ext)}")

    run_id = make_run_id("prepare", sha256_file(raw_file), sample_id, ref.name)
    plink_prefix = ws.root / "input" / sample_id
    eig_prefix = ws.root / "input" / f"{sample_id}_eigenstrat"
    merged_prefix = ws.root / "merged" / "merged"
    plink_prefix.parent.mkdir(parents=True, exist_ok=True)
    merged_prefix.parent.mkdir(parents=True, exist_ok=True)

    # 1. raw consumer file -> PLINK binary
    run_command(ws, [ws.plink, "--23file", raw_file, sample_id, sample_id,
                     "--make-bed", "--out", plink_prefix], "plink_convert", run_id)

    # 2. PLINK binary -> EIGENSTRAT
    par = write_parfile(ws.root / "input" / "convertf.par", {
        "genotypename": f"{plink_prefix}.bed",
        "snpname": f"{plink_prefix}.bim",
        "indivname": f"{plink_prefix}.fam",
        "outputformat": "EIGENSTRAT",
        "genotypeoutname": f"{eig_prefix}.geno",
        "snpoutname": f"{eig_prefix}.snp",
        "indivoutname": f"{eig_prefix}.ind",
    })
    run_command(ws, [ws.convertf, "-p", par], "convertf", run_id)
    set_population_label(_p(eig_prefix, ".ind"), sample_id)

    # 3. merge with the AADR reference
    par = write_parfile(ws.root / "merged" / "mergeit.par", {
        "geno1": f"{ref}.geno", "snp1": f"{ref}.snp", "ind1": f"{ref}.ind",
        "geno2": f"{eig_prefix}.geno", "snp2": f"{eig_prefix}.snp", "ind2": f"{eig_prefix}.ind",
        "genooutfilename": f"{merged_prefix}.geno",
        "snpoutfilename": f"{merged_prefix}.snp",
        "indoutfilename": f"{merged_prefix}.ind",
        "outputformat": "PACKEDANCESTRYMAP",
        "docheck": "YES",
        "hashcheck": "NO",
    })
    run_command(ws, [ws.mergeit, "-p", par], "mergeit", run_id)

    # 4. SNP accounting (counts only)
    qc = {
        "run_id": run_id,
        "sample_id": sample_id,
        "reference_prefix": str(ref),
        "raw_input_rows": count_lines(raw_file, skip_comments=True),
        "plink_variants": count_lines(_p(plink_prefix, ".bim")),
        "eigenstrat_snps": count_lines(_p(eig_prefix, ".snp")),
        "reference_snps": count_lines(_p(ref, ".snp")),
        "merged_snps": count_lines(_p(merged_prefix, ".snp")),
        "note": "Counts only. Inspect logs/ for allele-mismatch warnings from mergeit.",
    }
    (ws.root / "qc_report.json").write_text(json.dumps(qc, indent=2), encoding="utf-8")
    return merged_prefix
