#!/usr/bin/env python3
"""NOMS Fig. 3 — simulation-sweep scaling churn, faceted by prompt encoding.

Reads llm-k8s-autoscaler/plots/summary_long_sim.csv (the actual regenerated
sim sweep). One panel per encoding (small multiples, avoids needing 4
all-pairs-safe categorical hues); within each panel, one dot per model,
churn on a shared log x-axis. Single hue (validated palette slot 1).
"""
import csv

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

SRC = "/users/ffarazug/llm-k8s-autoscaler/plots/summary_long_sim.csv"

MODEL_ORDER = ["llama-8b", "llama4-scout", "llama-70b", "mistral-small4", "qwen3-80b", "gpt-oss-120b"]
MODEL_LABEL = {
    "llama-8b": "Llama-8B", "llama4-scout": "Llama4-Scout", "llama-70b": "Llama-70B",
    "mistral-small4": "Mistral-Small", "qwen3-80b": "Qwen3-80B", "gpt-oss-120b": "GPT-OSS-120B",
}
VARIANT_ORDER = ["zero_shot", "domain", "history_5", "cot"]
VARIANT_LABEL = {"zero_shot": "Zero-shot", "domain": "Domain", "history_5": "History", "cot": "Chain-of-thought"}

BLUE = "#2a78d6"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"

data = {}
with open(SRC) as fh:
    for row in csv.DictReader(fh):
        m, v = row["llm_model"], row["llm_variant"]
        if m in MODEL_ORDER and v in VARIANT_ORDER:
            data[(m, v)] = float(row["scale_events"])

fig, axes = plt.subplots(1, 4, figsize=(7.0, 2.5), dpi=300, sharey=True)
fig.patch.set_facecolor("#fcfcfb")

y_positions = list(range(len(MODEL_ORDER)))[::-1]

for ax, variant in zip(axes, VARIANT_ORDER):
    ax.set_facecolor("#fcfcfb")
    vals = [data[(m, variant)] for m in MODEL_ORDER]
    ax.scatter(vals, y_positions, s=32, color=BLUE, zorder=3, edgecolor="white", linewidth=0.5)
    for y, v in zip(y_positions, vals):
        ax.plot([1, v], [y, y], color=BLUE, lw=1, alpha=0.25, zorder=2)

    ax.set_xscale("log")
    ax.set_xlim(8, 2000)
    ax.set_title(VARIANT_LABEL[variant], fontsize=8, color=INK, pad=6)
    ax.xaxis.set_major_locator(mticker.LogLocator(base=10, numticks=3))
    ax.tick_params(axis="x", labelsize=6.3, colors=INK_SECONDARY)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", which="major", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)

axes[0].set_yticks(y_positions)
axes[0].set_yticklabels([MODEL_LABEL[m] for m in MODEL_ORDER], fontsize=7.4, color=INK)

fig.supxlabel("Scaling events over the 1,440-step trace (log scale)", fontsize=7.6, color=INK_SECONDARY, y=0.02)

fig.tight_layout(pad=0.6, rect=(0, 0.05, 1, 1))
fig.savefig("noms_fig3_sim_churn.pdf")
fig.savefig("noms_fig3_sim_churn.png", dpi=300)
print("saved noms_fig3_sim_churn.{pdf,png}")
