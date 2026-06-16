# Assignment 8 — Robustness Analysis

**Key methods:** Satisficing · Max regret · FaIR ensemble re-evaluation · PRIM scenario re-discovery

---

## Learning objectives

1. **Re-evaluate** candidate policies from Assignment 7 across a large ensemble of uncertain futures.
2. Compute **satisficing** and **regret** robustness metrics for each policy across all objectives.
3. Rank policies by their robustness score and identify the most robust policy.
4. Apply **scenario re-discovery** (PRIM) to identify the uncertain conditions under which even the most robust policies still fail.
5. Formulate a **policy recommendation** that accounts for both performance and robustness.

## Prerequisites

- **Assignment 6 completed** — the cross-seed reference set is required.
- **Assignment 7 completed** — the candidate policy shortlist is required.

:::{dropdown} Hint — JUSTICE uncertainties in re-evaluation
The re-evaluation uses the **FaIR climate ensemble** (1001 calibrated members, each representing a different Equilibrium Climate Sensitivity) to propagate physical uncertainty. This is one approach that can be combined with the normative uncertainties (ρ, η, δ) explored in Assignments 1–3.
:::

## Notebook

`assignments_ema/assignment_08_robustness.ipynb`
