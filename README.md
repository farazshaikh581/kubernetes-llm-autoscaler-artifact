# LLM-Based Kubernetes Autoscaling — Paper Artifact

Data, code, and reproduction scripts for the tables and figures in *"Tell the LLM What You Want: Intent-Driven Kubernetes Autoscaling"*

This repository is scoped to exactly what the paper reports: six open-weight
LLMs (Llama-8B, Llama-70B, Mistral-Small, GPT-OSS-120B, Qwen3-80B,
Llama4-Scout), four prompt variants each (zero-shot, domain-enriched,
history-augmented, chain-of-thought), against HPA, KEDA, DQN, and PPO
baselines, on a real k3s cluster and a calibrated queueing simulator. It does
not include exploratory work on additional models or workloads that isn't
part of this paper.

## What's here

```
.
├── k8s_autoscaler.py       # LLM autoscaler on the real cluster (Algorithm 1)
├── load_generator.py       # Trace-driven HTTP load generator
├── autoscale_env.py / _v2.py   # RL (DQN/PPO) training environment
├── train_rl.py / train_rl_v2.py # RL training and evaluation
├── extract_workload_traces.py   # Alibaba Cluster Trace 2018 -> RPS trace
├── requirements.txt
├── api_keys.conf.example
│
├── k8s/                    # Kubernetes manifests for the target workload
├── scripts/
│   ├── run_k8s_v2.sh       # Real-cluster experiment orchestration
│   └── run_long.sh         # 1,440-step simulation sweep
├── traces/                 # trace_cpu.npy (real cluster), trace_alibaba_1440.npy (sim)
│
├── results/long_sim/       # Simulation sweep, one CSV per (model, variant)
├── results_richer/cpu_bursty/  # Real-cluster raw per-step CSVs, 3 reps each
├── results_richer_cpu_bursty_*.csv  # Real-cluster summary/cost/percentile tables
│
└── plot_noms_fig_*.py      # Scripts that regenerate the paper's figures/tables from the above
```

## Reproducing the paper's figures and tables from the included data

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python plot_noms_fig_cost.py            # annualized cost figure
python plot_noms_fig_latency.py         # decision-latency figure
python plot_noms_fig_sim_validation.py  # simulator validation table
python plot_noms_fig2_variance.py       # per-repetition SLA variance figure
python plot_noms_fig3_sim_churn.py      # simulation churn figure
```

Table III (real-cluster and simulation results per controller and prompt
variant) is computed directly from `results_richer_cpu_bursty_summary.csv`,
`results_richer_cpu_bursty_business_case.csv`, and `results/long_sim/`.

## Re-running the experiments themselves

Requires API keys for at least one LLM provider (NVIDIA, Groq, or Cerebras)
and, for the real-cluster runs, a Kubernetes cluster.

```bash
cp api_keys.conf.example api_keys.conf   # add your keys

# Simulation sweep (no cluster needed)
bash scripts/run_long.sh

# Real-cluster experiment
kubectl apply -f k8s/workloads.yaml
bash scripts/run_k8s_v2.sh

# RL baselines
python train_rl_v2.py --algo dqn --timesteps 500000
python train_rl_v2.py --algo ppo --timesteps 500000
```

## Citation

This repository accompanies a paper currently under review. A full citation
will be added here once it is published; until then, please cite the
repository itself (see [CITATION.cff](CITATION.cff)).

## License

Licensed under CC BY 4.0 — see [LICENSE](LICENSE). You're free to use and
adapt this code and data, including commercially, as long as you credit the
paper/repo.
