#!/usr/bin/env python3
"""NOMS Fig. -- annualized cost per controller, cpu_bursty, real cluster.

Uses the VERIFIED cost_usd totals from results_richer_cpu_bursty_business_case.csv
(matches Table I closely: HPA $181 vs $183, PPO $701 vs $730). Zero-shot variant
for LLM models, to stay consistent with the other real-cluster figures in this
paper. No cost decomposition -- the per-token price constants that split this
into data/control/API parts aren't reliably reconstructable in this checkout,
and fresh web pricing contradicts the paper's own stated $0.07-0.69/Mtok range,
so this figure reports only what is directly verified.
"""
import csv

import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "dejavuserif",
    "axes.linewidth": 0.8,
    "pdf.fonttype": 42,
})

CONFIGS = [
    ("hpa", "baseline", "HPA", "rule"),
    ("keda", "baseline", "KEDA", "rule"),
    ("rl-dqn", "baseline", "DQN", "rl"),
    ("rl-ppo", "baseline", "PPO", "rl"),
    ("llama-8b", "zero_shot", "Llama-8B", "llm"),
    ("llama-70b", "zero_shot", "Llama-70B", "llm"),
    ("mistral-small4", "zero_shot", "Mistral-Small", "llm"),
    ("gpt-oss-120b", "zero_shot", "GPT-OSS-120B", "llm"),
]

CAT_COLOR = {"rule": "#2196F3", "rl": "#FF9800", "llm": "#4CAF50"}
CAT_LABEL = {"rule": "Rule-based", "rl": "Trained RL", "llm": "Frozen LLM (zero-shot)"}
INK = "#1a1a1a"
INK_SECONDARY = "#4a4a4a"
GRID = "#dcdcdc"

with open("results_richer_cpu_bursty_business_case.csv") as fh:
    rows = {(r["model"], r["variant"]): float(r["cost_usd"]) for r in csv.DictReader(fh)}

data = [(label, cat, rows[(model, variant)]) for model, variant, label, cat in CONFIGS]
data.sort(key=lambda d: d[2])

fig, ax = plt.subplots(figsize=(3.4, 3.1), dpi=400)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

y = list(range(len(data)))
labels = [d[0] for d in data]
vals = [d[2] for d in data]
colors = [CAT_COLOR[d[1]] for d in data]

bars = ax.barh(y, vals, color=colors, height=0.6, edgecolor="white", linewidth=0.6, zorder=3)
for yi, v in zip(y, vals):
    ax.text(v + 22, yi, f"\${v:,.0f}", fontsize=7.8, fontweight="bold", color=INK, va="center")

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=8.4, color=INK)
ax.set_xlim(0, max(vals) * 1.22)
ax.set_xlabel("Annualized cost ($/yr)", fontsize=8.4, color=INK_SECONDARY)
ax.tick_params(axis="x", labelsize=7.6, colors=INK_SECONDARY)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(GRID)

handles = [plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=CAT_COLOR[c],
                       markersize=7, label=CAT_LABEL[c]) for c in ["rule", "rl", "llm"]]
ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=7.2,
          handletextpad=0.4, borderaxespad=0.3)

fig.tight_layout(pad=0.5)
fig.savefig("noms_fig_cost.pdf", bbox_inches="tight")
fig.savefig("noms_fig_cost.png", dpi=400, bbox_inches="tight")
print("saved noms_fig_cost.{pdf,png}")
for label, cat, v in data:
    print(f"  {label:15s} \${v:,.0f}/yr")
