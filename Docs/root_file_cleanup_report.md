# Root File Cleanup Report

Static cleanup and path update report for loose project-root files. No files were permanently deleted. No model code was run. No plots were regenerated. No result data contents were modified. No commit was made.

## Files kept in root

| File | Reason |
| --- | --- |
| `final_project_youth_coalition.ipynb` | Main final notebook. |
| `README.md` | Project README. |

No root-level dependency files such as `.gitignore`, `requirements.txt`, `environment.yml`, or `pyproject.toml` were present at the time of this cleanup.

## Files moved to `scripts/`

| Original root path | New path | Reason |
| --- | --- | --- |
| `run_a02_sensitivity_traceable.py` | `scripts/run_a02_sensitivity_traceable.py` | Useful A2 traceability/reproducibility script. |
| `run_a03_1p5_traceable.py` | `scripts/run_a03_1p5_traceable.py` | Useful A3 traceability/reproducibility script. |
| `run_actor4_1p5_diagnostic.py` | `scripts/run_actor4_1p5_diagnostic.py` | Useful Actor 4 / 1.5 C diagnostic script. |
| `run_final_project_extra_figures.py` | `scripts/run_final_project_extra_figures.py` | Useful final-figure support script. |
| `run_reeval.py` | `scripts/run_reeval.py` | Useful re-evaluation script. |
| `run_reeval_actor4.py` | `scripts/run_reeval_actor4.py` | Useful Actor 4 re-evaluation script. |

## Files moved to `results/final_project/`

| Original root path | New path | Reason |
| --- | --- | --- |
| `selected_policies_actor4.csv` | `results/final_project/selected_policies_actor4.csv` | Final notebook input; belongs with final-project result data rather than loose in root. |

## Files moved to `archive_before_cleanup/root_loose_files/`

| Original root path | New path | Reason |
| --- | --- | --- |
| `main.py` | `archive_before_cleanup/root_loose_files/main.py` | Empty placeholder file; archived instead of deleted. |
| `run_reeval_original_backup.py` | `archive_before_cleanup/root_loose_files/run_reeval_original_backup.py` | Backup script; archived instead of deleted. |

## Notebook path replacements made

| Old reference | New reference |
| --- | --- |
| `run_a02_sensitivity_traceable.py` | `scripts/run_a02_sensitivity_traceable.py` |
| `run_final_project_extra_figures.py` | `scripts/run_final_project_extra_figures.py` |
| `PROJECT_ROOT / "selected_policies_actor4.csv"` fallback block | `PROJECT_ROOT / "results" / "final_project" / "selected_policies_actor4.csv"` |
| `Could not find selected_policies_actor4.csv in project root or results/` | `Could not find results/final_project/selected_policies_actor4.csv` |

The notebook now points directly to `results/final_project/selected_policies_actor4.csv`.

## Other reference updates

| File | Update |
| --- | --- |
| `README.md` | Updated selected-policy reference to `results/final_project/selected_policies_actor4.csv`. |
| Existing `Docs/` files | Checked for moved-file references; no broken script or selected-policy paths required updates in the Docs files currently present. |

## Unclear files

No loose root-level files remained unclear after inspection. Useful scripts were moved to `scripts/`; the final CSV was moved to `results/final_project/`; backup/placeholder files were archived.

## Confirmation

- Nothing was permanently deleted.
- No model code was run.
- No plots were regenerated.
- No result data contents were modified.
- No commit was made.
