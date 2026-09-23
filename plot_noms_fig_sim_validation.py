#!/usr/bin/env python3
"""NOMS Fig. — simulator validation against real telemetry (replaces the
churn-by-encoding figure and the Table sim_validation table in III-E).

A genuinely new concept relative to both prior figures and the magazine (which
has no simulation content at all): how much does hardening the queueing model
actually reduce prediction error against 2,400 real cluster steps. Numbers are
the exact values already in Table sim_validation in the .tex.
"""
import matplotlib.pyplot as plt

METRICS = [
    ("Latency P90", "ms", 304, 66),
    ("CPU utilization", "pp", 17.2, 9.7),
    ("Success rate", "pp", 3.2, 0.6),
]

LOSSLESS = "#9C27B0"   # magenta-purple, matches repo's established Material palette family
HARDENED = "#2196F3"   # blue
INK = "#1a1a1a"
INK_SECONDARY = "#4a4a4a"
GRID = "#dcdcdc"

fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.35), dpi=300)
fig.patch.set_facecolor("white")

for ax, (name, unit, lossless_v, hardened_v) in zip(axes, METRICS):
    ax.set_facecolor("white")
    xs = [0, 1]
    vals = [lossless_v, hardened_v]
    colors = [LOSSLESS, HARDENED]
    bars = ax.bar(xs, vals, width=0.62, color=colors, edgecolor="white", linewidth=0.6, zorder=3)

    for x, v in zip(xs, vals):
        ax.text(x, v + max(vals) * 0.035, f"{v:g}", ha="center", va="bottom",
                fontsize=8.6, fontweight="bold", color=INK)

    reduction = (lossless_v - hardened_v) / lossless_v * 100
    ax.text(0.5, max(vals) * 1.28, f"−{reduction:.0f}%", ha="center", va="bottom",
            fontsize=9.5, fontweight="bold", color="#0a7a3d")

    ax.set_xticks(xs)
    ax.set_xticklabels(["Lossless", "Hardened\n(this work)"], fontsize=7.6, color=INK)
    ax.set_title(f"{name} MAE ({unit})", fontsize=8.6, color=INK, fontweight="bold", pad=18)
    ax.set_ylim(0, max(vals) * 1.45)
    ax.tick_params(axis="y", labelsize=6.8, colors=INK_SECONDARY)
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)

fig.suptitle("", fontsize=1)
fig.text(0.5, -0.02,
          "Mean absolute error vs. 2,400 real-cluster CPU steps — SLA agreement improves 88.5% → 91.7%",
          ha="center", fontsize=7.4, color=INK_SECONDARY)

fig.tight_layout(pad=0.7, rect=(0, 0.04, 1, 1))
fig.savefig("noms_fig_sim_validation.pdf", bbox_inches="tight")
fig.savefig("noms_fig_sim_validation.png", dpi=300, bbox_inches="tight")
print("saved noms_fig_sim_validation.{pdf,png}")
