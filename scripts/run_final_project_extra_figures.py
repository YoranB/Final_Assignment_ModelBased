"""Generate traceable final-project supplemental figures.

This script recreates two older final-project figures from current project data:

- plots/final_project/fp_pareto_scatter_3panel.png
- plots/final_project/fp_robustness_ecs.png

It does not rerun optimisation, does not alter A5-A8 result files, and does not
copy old notebook PNGs. The ECS diagnostic is a lightweight deterministic
re-evaluation of the top-5 most climate-protective RBF policies from each
current reference set under three ECS ensemble members.
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

PROJECT_ROOT = Path(__file__).resolve().parent
COURSE_ROOT = PROJECT_ROOT / "epa141a"
JUSTICE_ROOT = COURSE_ROOT / "JUSTICE-main"
CONFIG_DIR = COURSE_ROOT / "config"
RESULTS_ROOT = PROJECT_ROOT / "results"
FINAL_RESULTS_DIR = RESULTS_ROOT / "final_project"
PLOTS_DIR = PROJECT_ROOT / "plots"
FINAL_PLOTS_DIR = PLOTS_DIR / "final_project"

PRIOR_PATH = RESULTS_ROOT / "reference_set_prioritarian_50000.csv"
UTIL_PATH = RESULTS_ROOT / "reference_set_utilitarian_50000.csv"

PARETO_SOURCE_PATH = FINAL_RESULTS_DIR / "fp_pareto_scatter_3panel_source.csv"
PARETO_PLOT_PATH = FINAL_PLOTS_DIR / "fp_pareto_scatter_3panel.png"
ECS_RESULTS_PATH = FINAL_RESULTS_DIR / "fp_robustness_ecs_results.csv"
ECS_SELECTED_PATH = FINAL_RESULTS_DIR / "fp_robustness_ecs_selected_policies.csv"
ECS_PLOT_PATH = FINAL_PLOTS_DIR / "fp_robustness_ecs.png"

if str(JUSTICE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUSTICE_ROOT))

import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

from justice.model import JUSTICE  # noqa: E402
from justice.objectives.objective_functions import years_above_temperature_threshold  # noqa: E402
from justice.util.data_loader import DataLoader  # noqa: E402
from justice.util.emission_control_constraint import EmissionControlConstraint  # noqa: E402
from justice.util.enumerations import Abatement, DamageFunction, Economy, WelfareFunction  # noqa: E402
from justice.util.model_time import TimeHorizon  # noqa: E402
from solvers.emodps.rbf import RBF  # noqa: E402


COLORS = {
    "PRIORITARIAN": "#2b7bba",
    "UTILITARIAN": "#e6862a",
}


def load_reference_sets() -> tuple[pd.DataFrame, pd.DataFrame]:
    prior = pd.read_csv(PRIOR_PATH)
    util = pd.read_csv(UTIL_PATH)
    prior["welfare_lens"] = "PRIORITARIAN"
    util["welfare_lens"] = "UTILITARIAN"
    prior["reference_set_row"] = prior.index
    util["reference_set_row"] = util.index
    return prior, util


def make_pareto_scatter(prior: pd.DataFrame, util: pd.DataFrame) -> dict[str, object]:
    FINAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    cols = [
        "welfare_lens",
        "reference_set_row",
        "fraction_above_threshold",
        "welfare_loss_damage",
        "welfare_loss_abatement",
    ]
    source = pd.concat([prior[cols], util[cols]], ignore_index=True)
    source.to_csv(PARETO_SOURCE_PATH, index=False)

    pairs = [
        (
            "fraction_above_threshold",
            "welfare_loss_damage",
            "Fraction above 2 degC threshold",
            "Welfare loss from damages",
        ),
        (
            "fraction_above_threshold",
            "welfare_loss_abatement",
            "Fraction above 2 degC threshold",
            "Welfare loss from abatement",
        ),
        (
            "welfare_loss_abatement",
            "welfare_loss_damage",
            "Welfare loss from abatement",
            "Welfare loss from damages",
        ),
    ]

    counts = source.groupby("welfare_lens").size().to_dict()
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    for ax, (x_col, y_col, x_label, y_label) in zip(axes, pairs):
        for lens in ["PRIORITARIAN", "UTILITARIAN"]:
            df = source[source["welfare_lens"] == lens]
            ax.scatter(
                df[x_col],
                df[y_col],
                s=28,
                alpha=0.72,
                color=COLORS[lens],
                edgecolor="white",
                linewidth=0.25,
                label=f"{lens} (n={counts.get(lens, 0)})",
            )
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(alpha=0.22)
        ax.legend(fontsize=8, frameon=False)
        sns.despine(ax=ax)

    fig.suptitle(
        "Pareto objective-space comparison: Prioritarian vs Utilitarian reference sets",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(PARETO_PLOT_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)

    ranges = {}
    for lens, df in source.groupby("welfare_lens"):
        ranges[lens] = {
            "n": int(len(df)),
            "fraction_min": float(df["fraction_above_threshold"].min()),
            "fraction_max": float(df["fraction_above_threshold"].max()),
            "damage_min": float(df["welfare_loss_damage"].min()),
            "damage_max": float(df["welfare_loss_damage"].max()),
            "abatement_min": float(df["welfare_loss_abatement"].min()),
            "abatement_max": float(df["welfare_loss_abatement"].max()),
        }
    return ranges


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

_CALIB_DF = pd.read_csv(JUSTICE_ROOT / "data" / "input" / "calibrated_constrained_parameters.csv")
_ECS_PROXY = _CALIB_DF["clim_F_4xCO2"] / (2.0 * _CALIB_DF["clim_kappa1"])
_SORTED_ORIG_INDICES = np.argsort(_ECS_PROXY.values) + 1


def ecs_percentile_to_ensemble(ecs_pct: float) -> int:
    rank = int(np.clip(round(float(ecs_pct) / 100.0 * 1000), 0, 1000))
    return int(_SORTED_ORIG_INDICES[rank])


def extract_decision_vector(row: pd.Series) -> np.ndarray:
    def get(prefix: str, idx: int) -> float:
        if f"{prefix}_{idx}" in row.index:
            return float(row[f"{prefix}_{idx}"])
        return float(row[f"{prefix} {idx}"])

    centers = np.array([get("center", i) for i in range(C_SHAPE[0])])
    radii = np.array([get("radii", i) for i in range(R_SHAPE[0])])
    weights = np.array([get("weights", i) for i in range(W_SHAPE[0])])
    return np.concatenate([centers, radii, weights])


def select_top5(reference_set: pd.DataFrame, welfare_lens: str) -> pd.DataFrame:
    selected = (
        reference_set.sort_values(
            ["fraction_above_threshold", "welfare_loss_damage"],
            ascending=[True, True],
        )
        .head(5)
        .copy()
    )
    selected["welfare_lens"] = welfare_lens
    selected["selection_rule"] = "lowest fraction_above_threshold, then lowest welfare_loss_damage"
    selected["selection_rank"] = range(1, len(selected) + 1)
    return selected


def evaluate_rbf_policy(policy_row: pd.Series, welfare_lens: str, ensemble_index: int) -> dict[str, float]:
    rbf = RBF(n_rbfs=N_RBFS, n_inputs=N_INPUTS, n_outputs=N_REGIONS)
    rbf.set_decision_vars(extract_decision_vector(policy_row))

    constraint = EmissionControlConstraint(
        max_annual_growth_rate=0.04,
        emission_control_start_timestep=EC_START_TS,
        min_emission_control_rate=0.01,
    )

    welfare = WelfareFunction[welfare_lens]
    old_cwd = Path.cwd()
    os.chdir(JUSTICE_ROOT)
    try:
        JUSTICE.hard_reset()
        model = JUSTICE(
            scenario=SCENARIO,
            climate_ensembles=[int(ensemble_index)],
            economy_type=Economy.NEOCLASSICAL,
            damage_function_type=DamageFunction.KALKUHL,
            abatement_type=Abatement.ENERDATA,
            social_welfare_function_type=welfare.value[0],
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
    finally:
        os.chdir(old_cwd)

    global_temperature = data["global_temperature"]
    return {
        "years_above_2C": float(years_above_temperature_threshold(global_temperature, 2.0)),
        "peak_global_temperature": float(np.nanmax(global_temperature)),
    }


def make_ecs_robustness(prior: pd.DataFrame, util: pd.DataFrame) -> pd.DataFrame:
    FINAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    selected = pd.concat(
        [
            select_top5(prior, "PRIORITARIAN"),
            select_top5(util, "UTILITARIAN"),
        ],
        ignore_index=True,
    )
    selected.to_csv(ECS_SELECTED_PATH, index=False)

    ecs_scenarios = [
        ("Low ECS approx. 2.5 degC", 20.0),
        ("Median ECS approx. 3.0 degC", 50.0),
        ("High ECS approx. 4.5 degC", 90.0),
    ]

    rows = []
    for _, policy in selected.iterrows():
        for ecs_label, ecs_percentile in ecs_scenarios:
            ensemble_index = ecs_percentile_to_ensemble(ecs_percentile)
            out = evaluate_rbf_policy(policy, policy["welfare_lens"], ensemble_index)
            rows.append(
                {
                    "welfare_lens": policy["welfare_lens"],
                    "reference_set_row": int(policy["reference_set_row"]),
                    "selection_rank": int(policy["selection_rank"]),
                    "selection_rule": policy["selection_rule"],
                    "ecs_label": ecs_label,
                    "ecs_percentile": ecs_percentile,
                    "climate_ensemble_index": ensemble_index,
                    "optimisation_fraction_above_threshold": float(policy["fraction_above_threshold"]),
                    "optimisation_welfare_loss_damage": float(policy["welfare_loss_damage"]),
                    "years_above_2C": out["years_above_2C"],
                    "peak_global_temperature": out["peak_global_temperature"],
                }
            )

    detail = pd.DataFrame(rows)
    detail.to_csv(ECS_RESULTS_PATH, index=False)
    make_ecs_plot(detail)
    return detail


def make_ecs_plot(detail: pd.DataFrame) -> None:
    ecs_order = [
        "Low ECS approx. 2.5 degC",
        "Median ECS approx. 3.0 degC",
        "High ECS approx. 4.5 degC",
    ]
    labels = ["Low ECS\n(~2.5 degC)", "Median ECS\n(~3.0 degC)", "High ECS\n(~4.5 degC)"]
    x = np.arange(len(ecs_order))
    width = 0.36

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    metrics = [
        ("years_above_2C", "Mean years above 2 degC", "Years above 2 degC"),
        ("peak_global_temperature", "Mean peak global temperature", "Peak temperature (degC)"),
    ]

    for ax, (metric, title, ylabel) in zip(axes, metrics):
        summary = (
            detail.groupby(["welfare_lens", "ecs_label"], as_index=False)[metric]
            .mean()
        )
        for offset, lens in [(-width / 2, "PRIORITARIAN"), (width / 2, "UTILITARIAN")]:
            values = []
            for ecs_label in ecs_order:
                match = summary[
                    (summary["welfare_lens"] == lens)
                    & (summary["ecs_label"] == ecs_label)
                ][metric]
                values.append(float(match.iloc[0]) if len(match) else np.nan)
            bars = ax.bar(
                x + offset,
                values,
                width,
                label=lens,
                color=COLORS[lens],
                alpha=0.88,
            )
            for bar, value in zip(bars, values):
                if np.isfinite(value):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        f"{value:.1f}" if metric == "peak_global_temperature" else f"{value:.0f}",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.22)
        ax.legend(frameon=False, fontsize=8)
        sns.despine(ax=ax)

    fig.suptitle(
        "Lightweight ECS diagnostic: top-5 climate-protective policies by welfare lens",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(ECS_PLOT_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    prior, util = load_reference_sets()
    ranges = make_pareto_scatter(prior, util)
    detail = make_ecs_robustness(prior, util)
    print("Saved:")
    for path in [PARETO_SOURCE_PATH, PARETO_PLOT_PATH, ECS_SELECTED_PATH, ECS_RESULTS_PATH, ECS_PLOT_PATH]:
        print(f"- {path.relative_to(PROJECT_ROOT)}")
    print("Pareto ranges:")
    print(json.dumps(ranges, indent=2))
    print("ECS summary:")
    print(
        detail.groupby(["welfare_lens", "ecs_label"])[
            ["years_above_2C", "peak_global_temperature"]
        ]
        .mean()
        .round(2)
    )


if __name__ == "__main__":
    main()
