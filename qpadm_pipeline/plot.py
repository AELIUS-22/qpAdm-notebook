"""Descriptive stacked-bar plot of qpAdm coefficients. Does not replace the model-fit test."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

LABELS = {"not_rejected": "not rejected at 0.05", "rejected": "REJECTED at 0.05",
          "infeasible_coefficients": "infeasible coefficients", "unknown": "fit unknown"}


def plot_results(rows: list, out_path) -> None:
    """rows: result dicts with target, sources, coefficients, p_value, model_status."""
    rows = [r for r in rows if r.get("coefficients")]
    if not rows:
        raise ValueError("No parsed results to plot.")
    sources = rows[0]["sources"]
    fig, ax = plt.subplots(figsize=(9, 1.6 + 0.7 * len(rows)))
    for i, r in enumerate(rows):
        left = 0.0
        for j, c in enumerate(r["coefficients"]):
            width = max(c, 0.0) * 100
            ax.barh(i, width, left=left, color=f"C{j}",
                    label=sources[j] if i == 0 and j < len(sources) else None)
            left += width
        p = r.get("p_value")
        tag = LABELS.get(r.get("model_status", "unknown"))
        p_txt = f"p={p:.4g}; " if p is not None else ""
        ax.text(101, i, f"{p_txt}{tag}", va="center", fontsize=8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["target"] for r in rows])
    ax.set_xlim(0, 100)
    ax.set_xlabel("qpAdm coefficient (%)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.35), ncol=3, fontsize=8, frameon=False)
    ax.set_title("qpAdm coefficients (descriptive; read together with model fit)", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
