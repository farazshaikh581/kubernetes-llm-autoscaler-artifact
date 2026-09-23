#!/usr/bin/env python3
"""NOMS Fig. 2 — real-cluster SLA by repetition (cpu_bursty).

Computes per-repetition SLA (share of steps with p90 latency < 200ms) directly
from raw results_richer/cpu_bursty/rep*/k8s_cpu_*.csv, for the 4 baselines plus
the zero-shot variant of each of the 4 LLM models. Dot/range plot: one row per
config, 3 rep dots + a range line, sorted by mean SLA. Colors follow the
dataviz-skill validated categorical palette (first 3 slots, all-pairs safe).
"""
import csv
import glob
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "dejavuserif",
    "axes.linewidth": 0.8,
    "pdf.fonttype": 42,
})

BASE = "results_richer/cpu_bursty"
REPS = ["rep1", "rep2", "rep3"]

# config key -> (display label, category)
CONFIGS = {
    "hpa_baseline": ("HPA", "rule"),
    "keda_baseline": ("KEDA", "rule"),
    "rl-dqn_baseline": ("DQN", "rl"),
    "rl-ppo_baseline": ("PPO", "rl"),
    "llama-8b_zero_shot": ("Llama-8B / zero-shot", "llm"),
    "llama-70b_zero_shot": ("Llama-70B / zero-shot", "llm"),
    "mistral-small4_zero_shot": ("Mistral-Small / zero-shot", "llm"),
    "gpt-oss-120b_zero_shot": ("GPT-OSS-120B / zero-shot", "llm"),
}

CAT_COLOR = {
    "rule": "#2196F3",  # blue — matches this paper's other figures
    "rl": "#FF9800",    # orange
    "llm": "#4CAF50",   # green
}
CAT_LABEL = {"rule": "Rule-based", "rl": "Trained RL", "llm": "Frozen LLM (zero-shot)"}

INK = "#1a1a1a"
INK_SECONDARY = "#4a4a4a"
INK_MUTED = "#7a7a7a"
GRID = "#dcdcdc"

data = {}
for key in CONFIGS:
    vals = []
    for rep in REPS:
        f = os.path.join(BASE, rep, f"k8s_cpu_{key}.csv")
        with open(f) as fh:
            rows = list(csv.DictReader(fh))
        lat = [float(r["latency_p90_ms"]) for r in rows if r["latency_p90_ms"] not in ("", "nan")]
        sla = sum(1 for v in lat if v < 200) / len(lat) * 100
        vals.append(sla)
    data[key] = vals

rows_sorted = sorted(CONFIGS, key=lambda k: -(sum(data[k]) / 3))

fig, ax = plt.subplots(figsize=(3.4, 3.5), dpi=400)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

ax.axvspan(99, 103, color="#4CAF50", alpha=0.07, zorder=0)

y_positions = list(range(len(rows_sorted)))[::-1]
labels = []
for y, key in zip(y_positions, rows_sorted):
    label, cat = CONFIGS[key]
    labels.append(label)
    vals = data[key]
    mean_v = sum(vals) / 3
    color = CAT_COLOR[cat]
    ax.plot([min(vals), max(vals)], [y, y], color=color, lw=1.6, alpha=0.85, zorder=2, solid_capstyle="round")
    ax.scatter(vals, [y] * 3, s=42, color=color, zorder=3, edgecolor="white", linewidth=0.7)
    ax.text(max(vals) + 2.5, y, f"{mean_v:.0f}%", fontsize=7.6, fontweight="bold",
            color=INK, ha="left", va="center")

ax.axvline(99, color=INK_MUTED, lw=0.9, ls=(0, (3, 2)), zorder=1)
ax.text(99.8, -1.15, "deployable $\\geq$ 99%", color="#2e7d32", fontsize=7.4,
        style="italic", ha="left", va="center")

ax.set_yticks(y_positions)
ax.set_yticklabels(labels, fontsize=8.4, color=INK)
ax.set_ylim(-1.7, len(rows_sorted) + 0.55)
ax.set_xlim(35, 118)
ax.set_xlabel("SLA compliance per repetition (%)", fontsize=8.4, color=INK_SECONDARY)
ax.xaxis.set_major_locator(mticker.MultipleLocator(20))
ax.tick_params(axis="x", labelsize=7.6, colors=INK_SECONDARY)
ax.tick_params(axis="y", length=0)

for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
ax.set_axisbelow(True)

handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=CAT_COLOR[c],
                       markersize=7, label=CAT_LABEL[c]) for c in ["rule", "rl", "llm"]]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.42, 1.0), ncol=1,
          frameon=False, fontsize=7.4, handletextpad=0.4, borderaxespad=0.1,
          columnspacing=0.8, labelspacing=0.35)

fig.tight_layout(pad=0.5)
fig.savefig("noms_fig2_variance.pdf", bbox_inches="tight")
fig.savefig("noms_fig2_variance.png", dpi=400, bbox_inches="tight")
print("saved noms_fig2_variance.{pdf,png}")
for key in rows_sorted:
    print(f"  {CONFIGS[key][0]:30s} mean={sum(data[key])/3:5.1f}  reps={[round(v,1) for v in data[key]]}")
