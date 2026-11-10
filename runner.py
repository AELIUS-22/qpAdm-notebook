"""Command runner and run ledger.

Every external command (PLINK, convertf, mergeit, qpAdm) goes through run_command().
It saves stdout/stderr to files, records the exit code and runtime, and appends a line
to the run ledger (JSON Lines) -- including failed attempts.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class PipelineError(RuntimeError):
    """Raised when an external step fails."""


@dataclass
class Workspace:
    """Working directory plus the names/paths of the external tools."""

    root: Path
    plink: str = "plink"
    convertf: str = "convertf"
    mergeit: str = "mergeit"
    qpadm: str = "qpAdm"

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.logs = self.root / "logs"
        self.ledger = self.root / "run_ledger.jsonl"
        self.logs.mkdir(parents=True, exist_ok=True)


def sha256_file(path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def make_run_id(*parts) -> str:
    """Deterministic short ID: same inputs -> same run ID."""
    joined = "|".join(str(p) for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:12]


def append_ledger(ws: Workspace, record: dict) -> None:
    with ws.ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


# Some ADMIXTOOLS programs can print a fatal error yet exit with code 0,
# so the exit code alone is not trusted.
FAILURE_MARKERS = ("fatal",)


def run_command(ws: Workspace, cmd: list, step: str, run_id: str,
                extra: dict | None = None, check: bool = True):
    """Run one command, log it, and return (record, stdout_text)."""
    stdout_path = ws.logs / f"{run_id}_{step}.stdout.txt"
    stderr_path = ws.logs / f"{run_id}_{step}.stderr.txt"
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    try:
        proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
        code, out, err = proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        code, out, err = 127, "", f"Executable not found: {exc}"
    runtime = round(time.perf_counter() - t0, 3)

    stdout_path.write_text(out, encoding="utf-8")
    stderr_path.write_text(err, encoding="utf-8")

    marker_hit = any(m in (out + err).lower() for m in FAILURE_MARKERS)
    status = "ok" if code == 0 and not marker_hit else "failed"

    record = {
        "type": "command",
        "run_id": run_id,
        "step": step,
        "command": [str(c) for c in cmd],
        "exit_code": code,
        "runtime_seconds": runtime,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "started_utc": started,
        "status": status,
        "extra": extra or {},
    }
    append_ledger(ws, record)  # written BEFORE any raise, so failures are kept

    if check and status != "ok":
        raise PipelineError(
            f"Step '{step}' failed (exit {code}). See {stderr_path} and {stdout_path}."
        )
    return record, out
