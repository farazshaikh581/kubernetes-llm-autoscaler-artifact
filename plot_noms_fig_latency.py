#!/usr/bin/env python3
"""NOMS Fig. -- LLM decision latency, real cluster, zero-shot, cpu_bursty.

Supports Contribution 4 (inference overhead / 6G edge feasibility), which
currently has zero supporting figure or table anywhere in the paper. Strip
plot of every individual real API call latency per model, log-scale x-axis,
with a reference line at the 60s control interval / cooldown.
"""
import csv
import glob
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "dejavuserif",
    "axes.linewidth": 0.8,
    "pdf.fonttype": 42,
})

BASE = "results_richer/cpu_bursty"
REPS = ["rep1", "rep2", "rep3"]
MODELS = [
    ("mistral-small4_zero_shot", "Mistral-Small"),
    ("llama-8b_zero_shot", "Llama-8B"),
    ("gpt-oss-120b_zero_shot", "GPT-OSS-120B"),
    ("llama-70b_zero_shot", "Llama-70B"),
]

INK = "#1a1a1a"
INK_SECONDARY = "#4a4a4a"
GRID = "#dcdcdc"
COLOR = "#4CAF50"
COLOR_WARN = "#e53935"

rng = np.random.default_rng(7)
data = {}
for key, label in MODELS:
    lat = []
    for rep in REPS:
        f = os.path.join(BASE, rep, f"k8s_cpu_{key}.csv")
        with open(f) as fh:
            rows = list(csv.DictReader(fh))
        lat.extend(float(r["llm_latency_ms"]) / 1000 for r in rows if r["llm_latency_ms"] not in ("", "nan"))
    data[label] = np.array(lat)

fig, ax = plt.subplots(figsize=(3.6, 2.9), dpi=400)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

ax.axvline(60, color=INK_SECONDARY, lw=1.1, ls=(0, (3, 2)), zorder=1)
ax.text(64, -0.52, "60 s control\ninterval", color=INK_SECONDARY, fontsize=7.2,
        style="italic", ha="left", va="bottom", linespacing=1.3)

for i, (key, label) in enumerate(MODELS):
    vals = data[label]
    y = i + rng.uniform(-0.16, 0.16, size=len(vals))
    over = vals > 60
    ax.scatter(vals[~over], y[~over], s=10, color=COLOR, alpha=0.5, zorder=3, linewidth=0)
    ax.scatter(vals[over], y[over], s=10, color=COLOR_WARN, alpha=0.7, zorder=3, linewidth=0)
    med = np.median(vals)
    ax.plot([med, med], [i - 0.3, i + 0.3], color=INK, lw=1.8, zorder=4)
    pct_over = (vals > 60).sum() / len(vals) * 100
    label_txt = f"median {med:.1f}s" + (f"  —  {pct_over:.0f}% of calls exceed 60s" if pct_over > 0 else "")
    ax.text(0.14, i + 0.38, label_txt, transform=ax.get_yaxis_transform(), fontsize=6.9,
            fontweight="bold", color=(COLOR_WARN if pct_over > 0 else INK), ha="left", va="bottom")

ax.set_xscale("log")
ax.set_xlim(0.1, 200)
ax.xaxis.set_major_locator(mticker.LogLocator(base=10))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
ax.set_xlabel("Decision latency, per call (s, log scale)", fontsize=8.4, color=INK_SECONDARY)
ax.set_yticks(range(len(MODELS)))
ax.set_yticklabels([m[1] for m in MODELS], fontsize=8.4, color=INK)
ax.set_ylim(-0.95, len(MODELS) - 0.05)
ax.tick_params(axis="x", labelsize=7.6, colors=INK_SECONDARY)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", which="major", color=GRID, lw=0.6, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(GRID)

fig.tight_layout(pad=0.5)
fig.savefig("noms_fig_latency.pdf", bbox_inches="tight")
fig.savefig("noms_fig_latency.png", dpi=400, bbox_inches="tight")
print("saved noms_fig_latency.{pdf,png}")
for key, label in MODELS:
    v = data[label]
    print(f"  {label:15s} n={len(v):4d} mean={v.mean():7.2f}s median={np.median(v):7.2f}s p90={np.percentile(v,90):7.2f}s over60={ (v>60).mean()*100:5.1f}%")
