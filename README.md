# Model-Based Decision Making Final Assignment

## Actor 4: Global Youth & Future Generations Coalition

## Purpose

This project uses the JUSTICE climate-economy model to evaluate climate-policy choices from the perspective of Global Youth and future generations. The final recommendation is developed through a Decision Making under Deep Uncertainty (DMDU) workflow that builds on Assignments 1-8: exploratory modelling, sensitivity analysis, scenario discovery, problem formulation, many-objective optimisation, convergence assessment, Pareto/policy selection, and robustness analysis.

## Main Deliverable

The main synthesis notebook is:

- `final_project_youth_coalition.ipynb`

Run this notebook from the project root. It is the report-oriented final notebook and is the primary file to review for the Part 1 model-based analysis and policy advice.

## Repository Structure

- `final_project_youth_coalition.ipynb` - main final synthesis notebook.
- `notebooks/assignments/` - supporting cleaned/working assignment notebooks used to generate or inspect A5-A8 analysis material.
- `notebooks/backups/` - backup copies of earlier final notebook versions.
- `notebooks/archive/` - old or superseded notebooks retained for traceability.
- `plots/` - assignment and project plots used by the final notebook.
- `plots/final_project/` - figures generated specifically for the final synthesis notebook.
- `results/` - optimisation reference sets, selected policies, robustness caches, and other saved model outputs.
- `results/final_project/` - final-project-specific generated CSV/data files.
- `Docs/` - project context, actor/rubric notes, and plot inventory documentation.
- `epa141a/` - embedded course repository containing the JUSTICE model, original assignment notebooks, model-answer references, and course materials.

## How to Run

1. Open the project root folder in VS Code, JupyterLab, or Jupyter Notebook.
2. Install and activate the same Python/Jupyter environment used for the EPA141A/JUSTICE course assignments before running the notebook.
3. Open and run `final_project_youth_coalition.ipynb` from the project root.
4. The notebook uses saved A5-A8 result files by default. It does not rerun heavy many-objective optimisation or robustness experiments during normal execution.

## Data and Cached Results

Heavy A5-A8 outputs are cached and reused for reproducibility and runtime practicality. Key saved files include:

- Optimisation reference sets and run outputs in `results/`.
- Selected policies, including `results/final_project/selected_policies_actor4.csv`.
- A8 robustness cache files, including the 5-policy by 50-scenario re-evaluation outputs in `results/`.
- Final-project generated CSVs in `results/final_project/`.
- Final synthesis figures in `plots/final_project/`.

## Reproducibility Notes

The final notebook uses relative paths from the project root. Keep `final_project_youth_coalition.ipynb` in the root unless path logic is updated and checked.

The `epa141a/` folder is retained because it contains the course JUSTICE model, original assignment notebooks, model-answer references, and supporting course materials needed to understand and reproduce the workflow.

Supporting notebooks in `notebooks/assignments/` may need their working directory set to the project root if run directly, because they were originally developed from the root folder.

## Main Analytical Conclusion

Among the evaluated policies, P0, the Actor-preferred Prioritarian policy, is the best available or least-bad option for the Global Youth & Future Generations Coalition. None of the evaluated policies is fully climate-safe. The analysis supports low/zero pure time preference and stronger mitigation from the Youth Coalition perspective.

## Important Caveat

Prioritarian vs Utilitarian is used as the main contrast because it captures the central low/zero-discount versus high-discount framing for intergenerational justice. The project does not claim that all possible welfare functions or all possible policy spaces were exhaustively optimised.


