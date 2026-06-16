"""Actor 4 selected-policy 1.5 degC diagnostic re-evaluation.

This is a diagnostic overlay for the final project. It does not rerun MOEA
optimisation, does not overwrite A5-A8 caches, and does not change selected
policies. It re-evaluates P0-P4 over the same 50 FAIR ensemble members used in
A8 and computes years above 1.5 degC plus a 2 degC comparison.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
COURSE_ROOT = PROJECT_ROOT / "epa141a"
JUSTICE_ROOT = COURSE_ROOT / "JUSTICE-main"
CONFIG_DIR = COURSE_ROOT / "config"
RESULTS_DIR = PROJECT_ROOT / "results"
FINAL_RESULTS_DIR = RESULTS_DIR / "final_project"
FINAL_PLOTS_DIR = PROJECT_ROOT / "plots" / "final_project"

if str(JUSTICE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUSTICE_ROOT))
os.chdir(JUSTICE_ROOT)

from justice.model import JUSTICE  # noqa: E402
from justice.util.data_loader import DataLoader  # noqa: E402
from justice.util.enumerations import Abatement, DamageFunction, Economy, WelfareFunction  # noqa: E402
from justice.util.emission_control_constraint import EmissionControlConstraint  # noqa: E402
from justice.util.model_time import TimeHorizon  # noqa: E402
from justice.objectives.objective_functions import years_above_temperature_threshold  # noqa: E402
from solvers.emodps.rbf import RBF  # noqa: E402

with (CONFIG_DIR / "config_ssp245.json").open("r", encoding="utf-8") as fh:
    CFG = json.load(fh)

TIME_HORIZON = TimeHorizon(
    start_year=CFG["start_year"],
    end_year=CFG["end_year"],
    data_timestep=CFG["data_timestep"],
    timestep=CFG["timestep"],
)
N_TIMESTEPS = len(TIME_HORIZON.model_time_horizon)
N_REGIONS = len(DataLoader().REGION_LIST)
N_INPUTS = CFG["n_inputs"]
N_RBFS = N_INPUTS + 2
SCENARIO = CFG["reference_ssp_rcp_scenario_index"]
EC_START_TS = TIME_HORIZON.year_to_timestep(
    year=CFG["emission_control_start_year"],
    timestep=CFG["timestep"],
)

_RBF_TMP = RBF(n_rbfs=N_RBFS, n_inputs=N_INPUTS, n_outputs=N_REGIONS)
C_SHAPE, R_SHAPE, W_SHAPE = _RBF_TMP.get_shape()
_MAX_TEMP, _MIN_TEMP = 16.0, 0.0
_MAX_DIFF, _MIN_DIFF = 2.0, 0.0

DETAIL_PATH = FINAL_RESULTS_DIR / "actor4_1p5_selected_policy_diagnostics.csv"
SUMMARY_PATH = FINAL_RESULTS_DIR / "actor4_1p5_selected_policy_summary.csv"
PLOT_PATH = FINAL_PLOTS_DIR / "a08_actor4_1p5_diagnostic_selected_policies.png"


def load_scenario_indices(n_scenarios: int) -> list[int]:
    experiments_path = RESULTS_DIR / "reeval_actor4_prioritarian_eval_5p_50s_experiments.csv"
    if experiments_path.exists():
        experiments = pd.read_csv(experiments_path)
        if "climate_ensemble_index" in experiments.columns:
            return sorted(int(x) for x in experiments["climate_ensemble_index"].dropna().unique())
    return list(np.linspace(1, 1000, n_scenarios, dtype=int))


def evaluate_policy(policy_row: pd.Series, ensemble_index: int) -> dict[str, float]:
    rbf = RBF(n_rbfs=N_RBFS, n_inputs=N_INPUTS, n_outputs=N_REGIONS)
    centers = np.array([float(policy_row[f"center_{i}"]) for i in range(C_SHAPE[0])])
    radii = np.array([float(policy_row[f"radii_{i}"]) for i in range(R_SHAPE[0])])
    weights = np.array([float(policy_row[f"weights_{i}"]) for i in range(W_SHAPE[0])])
    rbf.set_decision_vars(np.concatenate([centers, radii, weights]))

    constraint = EmissionControlConstraint(
        max_annual_growth_rate=0.04,
        emission_control_start_timestep=EC_START_TS,
        min_emission_control_rate=0.01,
    )

    model = JUSTICE(
        scenario=SCENARIO,
        climate_ensembles=[int(ensemble_index)],
        economy_type=Economy.NEOCLASSICAL,
        damage_function_type=DamageFunction.KALKUHL,
        abatement_type=Abatement.ENERDATA,
        social_welfare_function_type=WelfareFunction.PRIORITARIAN.value[0],
    )

    no_ens = model.no_of_ensembles
    ecr = np.zeros((N_REGIONS, N_TIMESTEPS, no_ens))
    constrained_ecr = np.zeros_like(ecr)
    prev_temp = np.zeros(no_ens)
    diff = np.zeros(no_ens)

    for t in range(N_TIMESTEPS):
        constrained_ecr[:, t, :] = constraint.constrain_emission_control_rate(
            ecr[:, t, :], t, allow_fallback=False
        )
        model.stepwise_run(
            emission_control_rate=constrained_ecr[:, t, :],
            timestep=t,
            endogenous_savings_rate=True,
        )
        data_t = model.stepwise_evaluate(timestep=t)
        temp = data_t["global_temperature"][t, :]

        if t % 5 == 0:
            diff = temp - prev_temp
            prev_temp = temp.copy()

        scaled_temp = (temp - _MIN_TEMP) / (_MAX_TEMP - _MIN_TEMP)
        scaled_diff = (diff - _MIN_DIFF) / (_MAX_DIFF - _MIN_DIFF)

        if t < N_TIMESTEPS - 1:
            ecr[:, t + 1, :] = rbf.apply_rbfs(np.array([scaled_temp, scaled_diff]))

    data = model.evaluate()
    global_temperature = data["global_temperature"]
    years_15 = float(years_above_temperature_threshold(global_temperature, threshold=1.5))
    years_20 = float(years_above_temperature_threshold(global_temperature, threshold=2.0))
    max_temp = float(np.nanmax(global_temperature))
    temp_2100 = float(global_temperature[TIME_HORIZON.year_to_timestep(2100, CFG["timestep"]), 0])

    return {
        "years_above_1p5C": years_15,
        "years_above_2C": years_20,
        "ever_above_1p5C": bool(years_15 > 0),
        "ever_above_2C": bool(years_20 > 0),
        "max_global_temperature": max_temp,
        "temperature_2100": temp_2100,
    }


def make_plot(detail: pd.DataFrame, summary: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    FINAL_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    order = list(summary.sort_values("policy_index")["policy"])
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    sns.boxplot(
        data=detail,
        x="policy",
        y="years_above_1p5C",
        order=order,
        color="#9ecae1",
        width=0.55,
        fliersize=2.5,
        ax=ax,
    )
    sns.stripplot(
        data=detail,
        x="policy",
        y="years_above_1p5C",
        order=order,
        color="#08519c",
        size=2.5,
        alpha=0.45,
        jitter=0.18,
        ax=ax,
    )
    medians = summary.set_index("policy").loc[order, "median_years_above_1p5C"]
    for i, value in enumerate(medians):
        ax.text(i, value + 3, f"med. {value:.0f}", ha="center", va="bottom", fontsize=8)
    ax.axhline(0, color="#444444", lw=1, ls="--")
    ax.set_title("Actor 4 diagnostic: years above 1.5 degC for selected policies")
    ax.set_xlabel("Selected policy")
    ax.set_ylabel("Years above 1.5 degC")
    ax.grid(axis="y", alpha=0.25)
    sns.despine(ax=ax)
    plt.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Actor 4 1.5 degC selected-policy diagnostic")
    parser.add_argument("--n_scenarios", type=int, default=50)
    parser.add_argument("--force", action="store_true", help="Overwrite existing diagnostic outputs")
    args = parser.parse_args()

    FINAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [DETAIL_PATH, SUMMARY_PATH, PLOT_PATH]
    existing = [p for p in outputs if p.exists()]
    if existing and not args.force:
        raise SystemExit("Diagnostic outputs already exist; use --force to regenerate: " + ", ".join(str(p) for p in existing))

    selected_path = PROJECT_ROOT / "selected_policies_actor4.csv"
    selected = pd.read_csv(selected_path)
    selected.columns = [c.replace(" ", "_") for c in selected.columns]
    selected.insert(0, "policy", [f"P{i}" for i in range(len(selected))])
    selected.insert(1, "policy_index", range(len(selected)))

    scenario_indices = load_scenario_indices(args.n_scenarios)
    print(f"Selected policies: {len(selected)}")
    print(f"Scenarios: {len(scenario_indices)} ({scenario_indices[:3]} ... {scenario_indices[-3:]})")

    records: list[dict[str, object]] = []
    total = len(selected) * len(scenario_indices)
    done = 0
    for _, policy_row in selected.iterrows():
        for scenario_pos, ensemble_index in enumerate(scenario_indices):
            done += 1
            print(f"[{done}/{total}] {policy_row['policy']} FAIR_{ensemble_index}", flush=True)
            metrics = evaluate_policy(policy_row, int(ensemble_index))
            records.append({
                "policy": policy_row["policy"],
                "policy_index": int(policy_row["policy_index"]),
                "selection_label": policy_row.get("selection_label", ""),
                "welfare_lens": policy_row.get("welfare_lens", ""),
                "run_name": policy_row.get("run_name", ""),
                "seed": policy_row.get("seed", ""),
                "scenario": f"FAIR_{ensemble_index}",
                "scenario_index": int(scenario_pos),
                "climate_ensemble_index": int(ensemble_index),
                **metrics,
            })

    detail = pd.DataFrame.from_records(records)
    detail.to_csv(DETAIL_PATH, index=False)

    summary = (
        detail.groupby(["policy", "policy_index", "selection_label", "welfare_lens"], dropna=False)
        .agg(
            median_years_above_1p5C=("years_above_1p5C", "median"),
            max_years_above_1p5C=("years_above_1p5C", "max"),
            min_years_above_1p5C=("years_above_1p5C", "min"),
            mean_years_above_1p5C=("years_above_1p5C", "mean"),
            share_scenarios_zero_years_above_1p5C=("years_above_1p5C", lambda s: float((s <= 0).mean())),
            median_years_above_2C=("years_above_2C", "median"),
            max_years_above_2C=("years_above_2C", "max"),
            min_years_above_2C=("years_above_2C", "min"),
            share_scenarios_zero_years_above_2C=("years_above_2C", lambda s: float((s <= 0).mean())),
            median_max_global_temperature=("max_global_temperature", "median"),
            n_scenarios=("scenario", "count"),
        )
        .reset_index()
        .sort_values("policy_index")
    )
    summary.to_csv(SUMMARY_PATH, index=False)
    make_plot(detail, summary)

    print("Saved detail:", DETAIL_PATH)
    print("Saved summary:", SUMMARY_PATH)
    print("Saved plot:", PLOT_PATH)
    print(summary[[
        "policy", "selection_label", "welfare_lens", "median_years_above_1p5C",
        "max_years_above_1p5C", "min_years_above_1p5C",
        "share_scenarios_zero_years_above_1p5C", "median_years_above_2C"
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
