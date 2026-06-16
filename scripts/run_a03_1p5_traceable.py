"""Traceable A3-inspired 1.5 degC scenario-discovery extension.

This script rebuilds the final-project A3 custom figures from code and saved data.
It is based on the official Assignment 3 workflow:

- epa141a/assignments_ema/assignment_03_scenario_discovery.ipynb
- epa141a/model_answers_ema/assignment_03_scenario_discovery_success_answer.ipynb

What is added here:
- years_above_1p5C, alongside the official years_above_2C-style diagnostic.
- A strict zero-exceedance success-rate comparison for 1.5 degC vs 2 degC.
- final-project CSV outputs under results/final_project/.

By default this script writes preview plots to plots/a03_traceable_rebuild_preview/
so existing recovered PNGs are not overwritten. Pass --write-final-plots to write the
final target plot paths in plots/.
"""

from __future__ import annotations

import argparse
import copy
import logging
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent
COURSE_ROOT = PROJECT_ROOT / "epa141a"
JUSTICE_ROOT = COURSE_ROOT / "JUSTICE-main"
PLOTS_DIR = PROJECT_ROOT / "plots"
RESULTS_DIR = PROJECT_ROOT / "results" / "final_project"
PREVIEW_PLOTS_DIR = PLOTS_DIR / "a03_traceable_rebuild_preview"

if str(JUSTICE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUSTICE_ROOT))

import matplotlib.path as _mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from ema_workbench import IntegerParameter, Model, RealParameter, Sample, ScalarOutcome, ema_logging
from ema_workbench.em_framework.evaluators import SequentialEvaluator

from justice.model import JUSTICE
from justice.objectives.objective_functions import years_above_temperature_threshold
from justice.util.enumerations import WelfareFunction

ema_logging.log_to_stderr(logging.WARNING)


def _path_deepcopy(self, memo=None):
    return copy.copy(self)


_mpath.Path.__deepcopy__ = _path_deepcopy

PARAMS = ["ssp_scenario", "ecs_percentile", "eta", "delta"]
POLICY_NAMES = ["low_abatement", "medium_abatement", "high_abatement"]
POLICY_PLATEAUS = [0.2, 0.5, 0.8]
POLICY_LABELS = {
    "low_abatement": "Low abatement",
    "medium_abatement": "Medium abatement",
    "high_abatement": "High abatement",
}
POLICY_COLORS = {
    "low_abatement": "#d95f02",
    "medium_abatement": "#7570b3",
    "high_abatement": "#1b9e77",
}

_calib_df = pd.read_csv(JUSTICE_ROOT / "data" / "input" / "calibrated_constrained_parameters.csv")
_ecs_proxy = _calib_df["clim_F_4xCO2"] / (2.0 * _calib_df["clim_kappa1"])
_sorted_orig_indices = np.argsort(_ecs_proxy.values) + 1


def ecs_percentile_to_ensemble(ecs_pct: float) -> int:
    rank = int(np.clip(round(float(ecs_pct) / 100.0 * 1000), 0, 1000))
    return int(_sorted_orig_indices[rank])


def justice_model(
    ssp_scenario: int = 2,
    ecs_percentile: float = 50.0,
    eta: float = 1.45,
    delta: float = 1.0,
    ecr_plateau: float = 0.5,
) -> dict[str, float]:
    """Official A3-style JUSTICE wrapper, extended with years_above_1p5C."""
    old_cwd = Path.cwd()
    os.chdir(JUSTICE_ROOT)
    try:
        JUSTICE.hard_reset()
        scenario_idx = int(np.round(np.clip(ssp_scenario, 0, 7)))
        ensemble_idx = ecs_percentile_to_ensemble(float(ecs_percentile))

        model = JUSTICE(
            start_year=2015,
            end_year=2300,
            timestep=1,
            scenario=scenario_idx,
            climate_ensembles=ensemble_idx,
            stochastic_run=False,
            social_welfare_function=WelfareFunction.UTILITARIAN,
        )

        # These assignments mirror the official A3 notebook/model-answer wrapper.
        model.welfare_function.pure_rate_of_social_time_preference = 0.015
        model.welfare_function.elasticity_of_marginal_utility_of_consumption = float(eta)
        model.damage_function.coefficient_a *= float(delta)
        model.damage_function.coefficient_b *= float(delta)
        model.damage_function.damage_gdp_ratio_with_gradient *= float(delta)

        years = np.arange(2015, 2301)
        tau = np.clip((years - 2015) / (2100 - 2015), 0, 1)
        s_curve = 3 * tau**2 - 2 * tau**3
        ecr = np.clip(np.outer(np.full(57, float(ecr_plateau)), s_curve), 0, 1)

        model.run(emission_control_rate=ecr, endogenous_savings_rate=True)
        datasets = model.evaluate()

        gt = datasets["global_temperature"]
        yat_15 = float(years_above_temperature_threshold(gt, 1.5))
        yat_2 = float(years_above_temperature_threshold(gt, 2.0))
        peak = float(np.max(gt))

        _, _, _, wl_dam = model.welfare_function.calculate_welfare(
            datasets["damage_cost_per_capita"], welfare_loss=True
        )

        return {
            "years_above_1p5C": yat_15,
            "years_above_2C": yat_2,
            "peak_temp": peak,
            "welfare_loss_damage": float(np.abs(wl_dam)),
        }
    finally:
        os.chdir(old_cwd)


def build_ema_model() -> Model:
    em_model = Model("JUSTICE_A3_1p5_extension", function=justice_model)
    em_model.uncertainties = [
        IntegerParameter("ssp_scenario", 0, 7),
        RealParameter("ecs_percentile", 0.0, 100.0),
        RealParameter("eta", 0.5, 2.5),
        RealParameter("delta", 0.5, 2.0),
    ]
    em_model.levers = [RealParameter("ecr_plateau", 0.1, 0.9)]
    em_model.outcomes = [
        ScalarOutcome("years_above_1p5C"),
        ScalarOutcome("years_above_2C"),
        ScalarOutcome("peak_temp"),
        ScalarOutcome("welfare_loss_damage"),
    ]
    return em_model


def run_experiments(n_scenarios: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    np.random.seed(seed)
    policies = [Sample(name, ecr_plateau=plateau) for name, plateau in zip(POLICY_NAMES, POLICY_PLATEAUS)]
    with SequentialEvaluator(build_ema_model()) as evaluator:
        experiments, outcomes = evaluator.perform_experiments(scenarios=n_scenarios, policies=policies)

    experiments_df = pd.DataFrame(experiments).copy()
    outcomes_df = pd.DataFrame(outcomes).copy()
    outcomes_df["policy"] = experiments_df["policy"].values
    outcomes_df["success_1p5C_zero_exceedance"] = outcomes_df["years_above_1p5C"] == 0
    outcomes_df["success_2C_zero_exceedance"] = outcomes_df["years_above_2C"] == 0
    return experiments_df, outcomes_df


def save_data(experiments_df: pd.DataFrame, outcomes_df: pd.DataFrame) -> pd.DataFrame:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    experiments_path = RESULTS_DIR / "a03_scenario_discovery_experiments.csv"
    outcomes_path = RESULTS_DIR / "a03_scenario_discovery_outcomes.csv"
    rates_path = RESULTS_DIR / "a03_scenario_discovery_success_rates.csv"

    experiments_df.to_csv(experiments_path, index=False)
    outcomes_df.to_csv(outcomes_path, index=False)

    rate_rows = []
    for policy, group in outcomes_df.groupby("policy", sort=False):
        rate_rows.append(
            {
                "policy": policy,
                "policy_label": POLICY_LABELS[policy],
                "threshold": "1.5 degC",
                "success_definition": "zero years above threshold",
                "success_rate": group["success_1p5C_zero_exceedance"].mean(),
                "n_success": int(group["success_1p5C_zero_exceedance"].sum()),
                "n_total": int(len(group)),
            }
        )
        rate_rows.append(
            {
                "policy": policy,
                "policy_label": POLICY_LABELS[policy],
                "threshold": "2 degC",
                "success_definition": "zero years above threshold",
                "success_rate": group["success_2C_zero_exceedance"].mean(),
                "n_success": int(group["success_2C_zero_exceedance"].sum()),
                "n_total": int(len(group)),
            }
        )
    rates = pd.DataFrame(rate_rows)
    rates.to_csv(rates_path, index=False)
    print(f"Saved {experiments_path}")
    print(f"Saved {outcomes_path}")
    print(f"Saved {rates_path}")
    return rates


def check_plot_targets(plot_dir: Path, overwrite: bool) -> None:
    targets = [
        plot_dir / "a03b_15c_vs_2c_success_rates.png",
        plot_dir / "a03b_scatter_15c_low_abatement.png",
        plot_dir / "a03b_scatter_15c_medium_abatement.png",
        plot_dir / "a03b_scatter_15c_high_abatement.png",
    ]
    existing = [p for p in targets if p.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing A3 plot files. "
            "Use --overwrite-plots only after preserving/reviewing them. Existing: "
            + ", ".join(str(p) for p in existing)
        )


def make_plots(experiments_df: pd.DataFrame, outcomes_df: pd.DataFrame, rates: pd.DataFrame, plot_dir: Path, overwrite: bool) -> None:
    plot_dir.mkdir(parents=True, exist_ok=True)
    check_plot_targets(plot_dir, overwrite=overwrite)

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    sns.barplot(
        data=rates,
        x="policy_label",
        y="success_rate",
        hue="threshold",
        palette={"1.5 degC": "#1f77b4", "2 degC": "#7f7f7f"},
        ax=ax,
    )
    ax.set_ylim(0, 1)
    ax.set_xlabel("")
    ax.set_ylabel("Share of scenarios with zero years above threshold")
    ax.set_title("A3 traceable extension: 1.5 degC success is harder than 2 degC")
    ax.legend(title="Threshold", frameon=False, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(plot_dir / "a03b_15c_vs_2c_success_rates.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    joined = outcomes_df.merge(
        experiments_df[["policy", "ssp_scenario", "ecs_percentile", "eta", "delta"]],
        left_index=True,
        right_index=True,
        suffixes=("", "_experiment"),
    )
    if "policy_experiment" in joined.columns:
        joined = joined.drop(columns=["policy_experiment"])

    for policy in POLICY_NAMES:
        group = joined[joined["policy"] == policy].copy()
        fig, ax = plt.subplots(figsize=(7.2, 5.0))
        sc = ax.scatter(
            group["ssp_scenario"],
            group["ecs_percentile"],
            c=group["years_above_1p5C"],
            cmap="magma_r",
            s=52,
            alpha=0.82,
            edgecolor=np.where(group["success_2C_zero_exceedance"], "black", "white"),
            linewidth=0.6,
        )
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label("Years above 1.5 degC")
        ax.set_xlabel("SSP scenario")
        ax.set_ylabel("ECS percentile")
        ax.set_xticks(range(8))
        ax.set_xticklabels([f"SSP{i}" for i in range(8)], rotation=45, fontsize=9)
        ax.set_ylim(-5, 105)
        ax.set_title(f"1.5 degC exceedance landscape - {POLICY_LABELS[policy]}")
        ax.text(
            0.02,
            0.98,
            "Black edge = zero years above 2 degC",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "0.85", "alpha": 0.9},
        )
        ax.grid(alpha=0.2)
        sns.despine(ax=ax)
        fig.tight_layout()
        fig.savefig(plot_dir / f"a03b_scatter_15c_{policy}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    print(f"Saved A3 plots to {plot_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run traceable A3 1.5 degC scenario-discovery extension.")
    parser.add_argument("--n-scenarios", type=int, default=200, help="Number of EMA scenarios per policy. Official A3 uses 200.")
    parser.add_argument("--seed", type=int, default=14103, help="NumPy seed set before EMA scenario generation.")
    parser.add_argument("--write-final-plots", action="store_true", help="Write plots to plots/ target filenames. Default writes preview plots.")
    parser.add_argument("--overwrite-plots", action="store_true", help="Allow overwriting existing plots in the selected plot directory.")
    args = parser.parse_args()

    plot_dir = PLOTS_DIR if args.write_final_plots else PREVIEW_PLOTS_DIR
    print("Traceable A3-inspired 1.5 degC extension")
    print(f"Scenarios per policy: {args.n_scenarios}")
    print(f"Seed: {args.seed}")
    print(f"Plot directory: {plot_dir}")

    experiments_df, outcomes_df = run_experiments(args.n_scenarios, args.seed)
    rates = save_data(experiments_df, outcomes_df)
    make_plots(experiments_df, outcomes_df, rates, plot_dir=plot_dir, overwrite=args.overwrite_plots)

    print("Success rates:")
    print(rates.pivot(index="policy_label", columns="threshold", values="success_rate").round(3))


if __name__ == "__main__":
    main()
