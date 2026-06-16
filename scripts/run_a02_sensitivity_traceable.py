"""Traceable Assignment 2 sensitivity-analysis rebuild for the final project.

Based on:
- epa141a/assignments_ema/assignment_02_sensitivity_analysis.ipynb
- epa141a/model_answers_ema/assignment_02_sensitivity_analysis_answer.ipynb

The script saves traceable CSV outputs before plotting and writes preview plots only to
plots/a02_traceable_rebuild_preview/. It does not overwrite the course/root A2 PNGs.
"""

from __future__ import annotations

import argparse
import copy
import logging
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent
COURSE_ROOT = PROJECT_ROOT / "epa141a"
JUSTICE_ROOT = COURSE_ROOT / "JUSTICE-main"
RESULTS_DIR = PROJECT_ROOT / "results" / "final_project"
PREVIEW_PLOTS_DIR = PROJECT_ROOT / "plots" / "a02_traceable_rebuild_preview"

if str(JUSTICE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUSTICE_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.path as _mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from SALib.analyze import morris as morris_analyze
from ema_workbench import ArrayOutcome, Model, RealParameter, Sample, ScalarOutcome, SequentialEvaluator, ema_logging
from ema_workbench.analysis import feature_scoring
from ema_workbench.em_framework.salib_samplers import MorrisSampler

from justice.model import JUSTICE
from justice.objectives.objective_functions import years_above_temperature_threshold
from justice.util.enumerations import WelfareFunction

ema_logging.log_to_stderr(logging.WARNING)


def _path_deepcopy(self, memo=None):
    return copy.copy(self)


_mpath.Path.__deepcopy__ = _path_deepcopy

OBJECTIVES = [
    "welfare",
    "years_above_temperature_threshold",
    "welfare_loss_damage",
    "welfare_loss_abatement",
]
PARAMS = ["rho", "eta", "delta", "ecs_ensemble"]
MORRIS_PARAMS = ["delta", "eta", "rho"]
POLICY_NAMES = ["no_abatement", "moderate_abatement"]
POLICY_ECR = {"no_abatement": 0.0, "moderate_abatement": 0.4}
ECS_MEDIAN = 501


def justice_model(rho=0.015, eta=1.45, delta=1.0, ecs_ensemble=1, ecr_plateau=0.0):
    """Official A2-style EMA Workbench JUSTICE wrapper."""
    old_cwd = Path.cwd()
    os.chdir(JUSTICE_ROOT)
    try:
        JUSTICE.hard_reset()
        ensemble_idx = int(np.round(np.clip(ecs_ensemble, 1, 1001)))
        model = JUSTICE(
            start_year=2015,
            end_year=2300,
            timestep=1,
            scenario=2,
            climate_ensembles=ensemble_idx,
            stochastic_run=False,
            social_welfare_function=WelfareFunction.UTILITARIAN,
        )
        model.economy.pure_rate_of_social_time_preference = float(rho)
        model.economy.elasticity_of_marginal_utility_of_consumption = float(eta)
        model.welfare_function.pure_rate_of_social_time_preference = float(rho)
        model.welfare_function.elasticity_of_marginal_utility_of_consumption = float(eta)
        model.damage_function.coefficient_a *= float(delta)
        model.damage_function.coefficient_b *= float(delta)
        model.damage_function.damage_gdp_ratio_with_gradient *= float(delta)

        ecr = np.full(model.emission_control_rate.shape[:2], float(ecr_plateau))
        model.run(emission_control_rate=ecr, endogenous_savings_rate=True)
        datasets = model.evaluate()

        welfare = float(np.abs(np.squeeze(datasets["welfare"])))
        yat = float(np.squeeze(years_above_temperature_threshold(datasets["global_temperature"], 2.0)))
        _, _, _, wl_dmg = model.welfare_function.calculate_welfare(
            datasets["damage_cost_per_capita"], welfare_loss=True
        )
        _, _, _, wl_abt = model.welfare_function.calculate_welfare(
            datasets["abatement_cost_per_capita"], welfare_loss=True
        )
        temp = np.squeeze(datasets["global_temperature"])
        if getattr(temp, "ndim", 0) == 2:
            temp = temp.mean(axis=0)

        return {
            "welfare": welfare,
            "years_above_temperature_threshold": yat,
            "welfare_loss_damage": float(np.abs(np.squeeze(wl_dmg))),
            "welfare_loss_abatement": float(np.abs(np.squeeze(wl_abt))),
            "temperature_trajectory": temp.astype(float),
        }
    finally:
        os.chdir(old_cwd)


def build_lhs_model() -> Model:
    em_model = Model("JUSTICE_A2_traceable", function=justice_model)
    em_model.uncertainties = [
        RealParameter("rho", 0.001, 0.030),
        RealParameter("eta", 0.5, 1.5),
        RealParameter("delta", 0.5, 2.0),
        RealParameter("ecs_ensemble", 1, 1001),
    ]
    em_model.levers = [RealParameter("ecr_plateau", 0.0, 1.0)]
    em_model.outcomes = [
        ScalarOutcome("welfare"),
        ScalarOutcome("years_above_temperature_threshold"),
        ScalarOutcome("welfare_loss_damage"),
        ScalarOutcome("welfare_loss_abatement"),
        ArrayOutcome("temperature_trajectory"),
    ]
    return em_model


def build_morris_model() -> Model:
    def justice_model_morris(rho=0.015, eta=1.45, delta=1.0, ecr_plateau=0.0):
        return justice_model(
            rho=rho,
            eta=eta,
            delta=delta,
            ecs_ensemble=ECS_MEDIAN,
            ecr_plateau=ecr_plateau,
        )

    em_model = Model("JUSTICE_A2_morris_traceable", function=justice_model_morris)
    em_model.uncertainties = [
        RealParameter("delta", 0.5, 2.0),
        RealParameter("eta", 0.5, 1.5),
        RealParameter("rho", 0.001, 0.030),
    ]
    em_model.levers = [RealParameter("ecr_plateau", 0.0, 1.0)]
    em_model.outcomes = [ScalarOutcome(o) for o in OBJECTIVES]
    return em_model


def run_lhs(n_lhs: int, seed: int):
    np.random.seed(seed)
    policies = [Sample(name, ecr_plateau=POLICY_ECR[name]) for name in POLICY_NAMES]
    with SequentialEvaluator(build_lhs_model()) as evaluator:
        experiments, outcomes = evaluator.perform_experiments(scenarios=n_lhs, policies=policies)
    experiments_df = pd.DataFrame(experiments).copy()
    outcomes_df = pd.DataFrame({k: v for k, v in outcomes.items() if k != "temperature_trajectory"}).copy()
    outcomes_df["policy"] = experiments_df["policy"].values
    return experiments_df, outcomes_df, outcomes


def compute_extra_trees(experiments_df: pd.DataFrame, outcomes: dict) -> pd.DataFrame:
    rows = []
    for pol in POLICY_NAMES:
        mask = experiments_df["policy"] == pol
        x_pol = experiments_df.loc[mask, PARAMS]
        y_pol = {k: np.asarray(outcomes[k])[mask.values] for k in OBJECTIVES}
        scores = feature_scoring.get_feature_scores_all(x_pol, y_pol)
        for parameter in PARAMS:
            for outcome in OBJECTIVES:
                rows.append(
                    {
                        "policy": pol,
                        "parameter": parameter,
                        "outcome": outcome,
                        "importance": float(scores.loc[parameter, outcome]),
                    }
                )
    return pd.DataFrame(rows)


def run_morris(n_morris: int, seed: int):
    np.random.seed(seed)
    morris_problem = {
        "num_vars": 3,
        "names": MORRIS_PARAMS,
        "bounds": [[0.5, 2.0], [0.5, 1.5], [0.001, 0.030]],
    }
    all_experiments = []
    all_outcomes = []
    indices_rows = []

    for pol in POLICY_NAMES:
        with SequentialEvaluator(build_morris_model()) as evaluator:
            experiments, outcomes = evaluator.perform_experiments(
                scenarios=n_morris,
                uncertainty_sampling=MorrisSampler(),
                policies=[Sample(pol, ecr_plateau=POLICY_ECR[pol])],
            )
        experiments_df = pd.DataFrame(experiments).copy()
        outcomes_df = pd.DataFrame({k: v for k, v in outcomes.items() if k != "temperature_trajectory"}).copy()
        outcomes_df["policy"] = experiments_df["policy"].values
        all_experiments.append(experiments_df)
        all_outcomes.append(outcomes_df)

        X = experiments_df[MORRIS_PARAMS].values
        for outcome in OBJECTIVES:
            Si = morris_analyze.analyze(morris_problem, X, outcomes[outcome], print_to_console=False)
            for i, parameter in enumerate(MORRIS_PARAMS):
                indices_rows.append(
                    {
                        "policy": pol,
                        "outcome": outcome,
                        "parameter": parameter,
                        "mu": float(Si["mu"][i]),
                        "mu_star": float(Si["mu_star"][i]),
                        "sigma": float(Si["sigma"][i]),
                    }
                )
    return pd.concat(all_experiments, ignore_index=True), pd.concat(all_outcomes, ignore_index=True), pd.DataFrame(indices_rows)


def save_outputs(lhs_experiments, lhs_outcomes, et_importance, morris_experiments, morris_outcomes, morris_indices):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    lhs_experiments.to_csv(RESULTS_DIR / "a02_sensitivity_experiments.csv", index=False)
    lhs_outcomes.to_csv(RESULTS_DIR / "a02_sensitivity_outcomes.csv", index=False)
    et_importance.to_csv(RESULTS_DIR / "a02_extra_trees_importance.csv", index=False)
    morris_experiments.to_csv(RESULTS_DIR / "a02_morris_experiments.csv", index=False)
    morris_outcomes.to_csv(RESULTS_DIR / "a02_morris_outcomes.csv", index=False)
    morris_indices.to_csv(RESULTS_DIR / "a02_morris_indices.csv", index=False)


def plot_extra_trees(et_importance: pd.DataFrame):
    PREVIEW_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    colors = ["#4C9BE8", "#E87B4C", "#4CE87B", "#BE4CE8"]
    pol = "moderate_abatement"
    sc = et_importance[et_importance["policy"] == pol].pivot(index="parameter", columns="outcome", values="importance")
    x = np.arange(len(PARAMS))
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, obj in zip(axes.flat, OBJECTIVES):
        imp = sc[obj].reindex(PARAMS).values
        bars = ax.bar(x, imp, color=colors, edgecolor="white", width=0.6)
        ax.set_xticks(x)
        ax.set_xticklabels(PARAMS, rotation=15, fontsize=9)
        ax.set_ylim(0, 1.05)
        ax.set_title(obj.replace("_", " "), fontsize=10)
        ax.set_ylabel("Importance")
        ax.axhline(0.25, color="grey", lw=0.8, ls="--")
        for bar, val in zip(bars, imp):
            if np.isfinite(val):
                ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f"{val:.2f}", ha="center", va="bottom", fontsize=8)
    fig.suptitle("Extra-Trees feature importance - moderate abatement (traceable A2 rebuild)", fontsize=12)
    plt.tight_layout()
    fig.savefig(PREVIEW_PLOTS_DIR / "a02ema_et_moderate_abatement.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_heatmap(et_importance: pd.DataFrame):
    short = [o.replace("years_above_temperature_threshold", "yrs > 2 degC").replace("welfare_loss_", "wl_") for o in OBJECTIVES]
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    for ax, pol in zip(axes, POLICY_NAMES):
        mat = et_importance[et_importance["policy"] == pol].pivot(index="parameter", columns="outcome", values="importance").reindex(PARAMS)[OBJECTIVES]
        mat_norm = (mat / mat.sum()).fillna(0)
        sns.heatmap(mat_norm, annot=True, fmt=".2f", cmap="YlOrRd", vmin=0, vmax=1, linewidths=0.5, ax=ax, annot_kws={"size": 11})
        ax.set_title(f"Extra-Trees importance (normalised)\n{pol.replace('_', ' ')}", fontsize=11)
        ax.set_xlabel("Outcome")
        ax.set_ylabel("Parameter")
        ax.set_xticklabels(short, rotation=20, ha="right")
    fig.suptitle("Policy-conditional sensitivity - Extra-Trees feature importance (traceable A2 rebuild)", fontsize=12)
    plt.tight_layout()
    fig.savefig(PREVIEW_PLOTS_DIR / "a02ema_sensitivity_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_morris(morris_indices: pd.DataFrame, n_morris: int):
    pol = "moderate_abatement"
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    x = np.arange(len(MORRIS_PARAMS))
    colors = ["#4C9BE8", "#E87B4C", "#4CE87B"]
    for ax, obj in zip(axes.flat, OBJECTIVES):
        sub = morris_indices[(morris_indices["policy"] == pol) & (morris_indices["outcome"] == obj)].set_index("parameter").reindex(MORRIS_PARAMS)
        mu_star = sub["mu_star"].values
        sigma = sub["sigma"].values
        bars = ax.bar(x, mu_star, color=colors, edgecolor="white", width=0.5, label="mu*")
        ax.scatter(x, sigma, color="black", zorder=5, s=40, marker="D", label="sigma")
        for xi, (m, s) in enumerate(zip(mu_star, sigma)):
            if np.isfinite(m) and np.isfinite(s):
                ax.vlines(xi, m, s, colors="black", lw=1.5, linestyles="dashed")
        ax.set_xticks(x)
        ax.set_xticklabels(MORRIS_PARAMS, rotation=15)
        ax.set_title(obj.replace("_", " "), fontsize=10)
        ax.set_ylabel("mu* / sigma")
        ax.legend(fontsize=7)
        ylim_top = ax.get_ylim()[1]
        for bar, val in zip(bars, mu_star):
            if np.isfinite(val):
                ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01 * ylim_top, f"{val:.0f}", ha="center", va="bottom", fontsize=7)
    fig.suptitle(
        f"Morris elementary effects - moderate abatement\n3 normative parameters, N={n_morris} (ecs_ensemble fixed at median) - traceable A2 rebuild",
        fontsize=11,
    )
    plt.tight_layout()
    fig.savefig(PREVIEW_PLOTS_DIR / "a02ema_morris_moderate_abatement.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def make_plots(et_importance: pd.DataFrame, morris_indices: pd.DataFrame, n_morris: int):
    PREVIEW_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    plot_extra_trees(et_importance)
    plot_heatmap(et_importance)
    plot_morris(morris_indices, n_morris)


def main():
    parser = argparse.ArgumentParser(description="Traceable A2 sensitivity-analysis rebuild.")
    parser.add_argument("--n-lhs", type=int, default=100, help="LHS scenarios per policy. Official A2 uses 100.")
    parser.add_argument("--n-morris", type=int, default=50, help="Morris trajectories per policy. Official A2 uses 50.")
    parser.add_argument("--seed", type=int, default=14102, help="NumPy seed before each experiment design.")
    args = parser.parse_args()

    start = time.perf_counter()
    print("Traceable A2 sensitivity rebuild")
    print(f"n_lhs={args.n_lhs}, n_morris={args.n_morris}, seed={args.seed}")

    lhs_experiments, lhs_outcomes, raw_lhs_outcomes = run_lhs(args.n_lhs, args.seed)
    et_importance = compute_extra_trees(lhs_experiments, raw_lhs_outcomes)
    morris_experiments, morris_outcomes, morris_indices = run_morris(args.n_morris, args.seed + 1)
    save_outputs(lhs_experiments, lhs_outcomes, et_importance, morris_experiments, morris_outcomes, morris_indices)
    make_plots(et_importance, morris_indices, args.n_morris)

    print("Saved CSV outputs to", RESULTS_DIR)
    print("Saved preview plots to", PREVIEW_PLOTS_DIR)
    print("Rows:")
    print(f"  LHS experiments: {len(lhs_experiments)}")
    print(f"  LHS outcomes: {len(lhs_outcomes)}")
    print(f"  Extra Trees rows: {len(et_importance)}")
    print(f"  Morris experiments: {len(morris_experiments)}")
    print(f"  Morris outcomes: {len(morris_outcomes)}")
    print(f"  Morris index rows: {len(morris_indices)}")
    print("Moderate-abatement Extra Trees sample:")
    print(et_importance[et_importance["policy"] == "moderate_abatement"].head().round(4).to_string(index=False))
    print("Moderate-abatement Morris sample:")
    print(morris_indices[morris_indices["policy"] == "moderate_abatement"].head().round(4).to_string(index=False))
    print(f"Runtime seconds: {time.perf_counter() - start:.1f}")


if __name__ == "__main__":
    main()
