## 1. Plots directly used by the final notebook

These plot paths are referenced in `final_project_youth_coalition.ipynb`, either as literal paths or as paths assembled from `PLOTS_DIR` / `FINAL_PLOTS_DIR`.

- `plots/final_project/fp_welfare_comparison.png`
- `plots/final_project/fp_discount_weighted_damage_prioritarian_vs_utilitarian.png`
- `plots/a02_traceable_rebuild_preview/a02ema_sensitivity_heatmap.png`
- `plots/a02_traceable_rebuild_preview/a02ema_et_moderate_abatement.png`
- `plots/a02_traceable_rebuild_preview/a02ema_morris_moderate_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style/a03b_15c_vs_2c_success_rates.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_low_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_medium_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_high_abatement.png`
- `plots/a06_convergence_prioritarian_50000.png`
- `plots/a06_convergence_utilitarian_50000.png`
- `plots/a07_pareto_prioritarian_vs_utilitarian.png`
- `plots/a07_parallel_coordinates_objectives.png`
- `plots/a07_actor_preferred_policy.png`
- `plots/a07_threshold_distribution_by_lens.png`
- `plots/final_project/fp_pareto_scatter_3panel.png`
- `plots/a08_actor4_minimax_regret_ranking.png`
- `plots/a08_actor4_satisficing_heatmap.png`
- `plots/a08_actor4_regret_cdf.png`
- `plots/final_project/a08_actor4_1p5_diagnostic_selected_policies.png`
- `plots/final_project/fp_robustness_ecs.png`

## 2. Plot files/folders that must stay

These exact files and containing folders must remain at their current paths unless the notebook paths are updated.

- `plots/`
- `plots/a02_traceable_rebuild_preview/`
- `plots/a02_traceable_rebuild_preview/a02ema_sensitivity_heatmap.png`
- `plots/a02_traceable_rebuild_preview/a02ema_et_moderate_abatement.png`
- `plots/a02_traceable_rebuild_preview/a02ema_morris_moderate_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style/`
- `plots/a03_traceable_rebuild_preview_assignment3_style/a03b_15c_vs_2c_success_rates.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style_v2/`
- `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_low_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_medium_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_high_abatement.png`
- `plots/a06_convergence_prioritarian_50000.png`
- `plots/a06_convergence_utilitarian_50000.png`
- `plots/a07_pareto_prioritarian_vs_utilitarian.png`
- `plots/a07_parallel_coordinates_objectives.png`
- `plots/a07_actor_preferred_policy.png`
- `plots/a07_threshold_distribution_by_lens.png`
- `plots/a08_actor4_minimax_regret_ranking.png`
- `plots/a08_actor4_satisficing_heatmap.png`
- `plots/a08_actor4_regret_cdf.png`
- `plots/final_project/`
- `plots/final_project/fp_welfare_comparison.png`
- `plots/final_project/fp_discount_weighted_damage_prioritarian_vs_utilitarian.png`
- `plots/final_project/fp_pareto_scatter_3panel.png`
- `plots/final_project/a08_actor4_1p5_diagnostic_selected_policies.png`
- `plots/final_project/fp_robustness_ecs.png`

## 3. Plot files/folders that appear unused

These files and folders are present in `plots/` but were not referenced anywhere in `final_project_youth_coalition.ipynb`.

- `plots/a03_traceable_rebuild_preview/`
- `plots/a03_traceable_rebuild_preview/a03b_15c_vs_2c_success_rates.png`
- `plots/a03_traceable_rebuild_preview/a03b_scatter_15c_high_abatement.png`
- `plots/a03_traceable_rebuild_preview/a03b_scatter_15c_low_abatement.png`
- `plots/a03_traceable_rebuild_preview/a03b_scatter_15c_medium_abatement.png`
- `plots/a02ema_et_moderate_abatement.png`
- `plots/a02ema_morris_moderate_abatement.png`
- `plots/a02ema_sensitivity_heatmap.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style/a03b_scatter_15c_high_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style/a03b_scatter_15c_low_abatement.png`
- `plots/a03_traceable_rebuild_preview_assignment3_style/a03b_scatter_15c_medium_abatement.png`
- `plots/a03b_15c_vs_2c_success_rates.png`
- `plots/a03b_scatter_15c_high_abatement.png`
- `plots/a03b_scatter_15c_low_abatement.png`
- `plots/a03b_scatter_15c_medium_abatement.png`
- `plots/a07_abatement_vs_threshold_risk.png`
- `plots/a07_parallel_coordinates_all_fronts.png`
- `plots/a07_pareto_faceted_by_welfare_lens.png`
- `plots/a07_pareto_solution_counts.png`
- `plots/final_project/fp_robustness_ecs_P0_P3_P4.png`

## 4. If I want only `plots/final_project/` to remain

These currently-used plots outside `plots/final_project/` would need to be copied into `plots/final_project/`, and the notebook would need the corresponding path replacements.

| Current used path | Copy target | Notebook path replacement |
| --- | --- | --- |
| `plots/a02_traceable_rebuild_preview/a02ema_sensitivity_heatmap.png` | `plots/final_project/a02ema_sensitivity_heatmap.png` | Replace with `plots/final_project/a02ema_sensitivity_heatmap.png`. |
| `plots/a02_traceable_rebuild_preview/a02ema_et_moderate_abatement.png` | `plots/final_project/a02ema_et_moderate_abatement.png` | Replace with `plots/final_project/a02ema_et_moderate_abatement.png`. |
| `plots/a02_traceable_rebuild_preview/a02ema_morris_moderate_abatement.png` | `plots/final_project/a02ema_morris_moderate_abatement.png` | Replace with `plots/final_project/a02ema_morris_moderate_abatement.png`. |
| `plots/a03_traceable_rebuild_preview_assignment3_style/a03b_15c_vs_2c_success_rates.png` | `plots/final_project/a03b_15c_vs_2c_success_rates.png` | Replace with `plots/final_project/a03b_15c_vs_2c_success_rates.png`. |
| `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_low_abatement.png` | `plots/final_project/a03b_scatter_15c_low_abatement.png` | Replace with `plots/final_project/a03b_scatter_15c_low_abatement.png`. |
| `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_medium_abatement.png` | `plots/final_project/a03b_scatter_15c_medium_abatement.png` | Replace with `plots/final_project/a03b_scatter_15c_medium_abatement.png`. |
| `plots/a03_traceable_rebuild_preview_assignment3_style_v2/a03b_scatter_15c_high_abatement.png` | `plots/final_project/a03b_scatter_15c_high_abatement.png` | Replace with `plots/final_project/a03b_scatter_15c_high_abatement.png`. |
| `plots/a06_convergence_prioritarian_50000.png` | `plots/final_project/a06_convergence_prioritarian_50000.png` | Replace with `plots/final_project/a06_convergence_prioritarian_50000.png`. |
| `plots/a06_convergence_utilitarian_50000.png` | `plots/final_project/a06_convergence_utilitarian_50000.png` | Replace with `plots/final_project/a06_convergence_utilitarian_50000.png`. |
| `plots/a07_pareto_prioritarian_vs_utilitarian.png` | `plots/final_project/a07_pareto_prioritarian_vs_utilitarian.png` | Replace with `plots/final_project/a07_pareto_prioritarian_vs_utilitarian.png`. |
| `plots/a07_parallel_coordinates_objectives.png` | `plots/final_project/a07_parallel_coordinates_objectives.png` | Replace with `plots/final_project/a07_parallel_coordinates_objectives.png`. |
| `plots/a07_actor_preferred_policy.png` | `plots/final_project/a07_actor_preferred_policy.png` | Replace with `plots/final_project/a07_actor_preferred_policy.png`. |
| `plots/a07_threshold_distribution_by_lens.png` | `plots/final_project/a07_threshold_distribution_by_lens.png` | Replace with `plots/final_project/a07_threshold_distribution_by_lens.png`. |
| `plots/a08_actor4_minimax_regret_ranking.png` | `plots/final_project/a08_actor4_minimax_regret_ranking.png` | Replace with `plots/final_project/a08_actor4_minimax_regret_ranking.png`. |
| `plots/a08_actor4_satisficing_heatmap.png` | `plots/final_project/a08_actor4_satisficing_heatmap.png` | Replace with `plots/final_project/a08_actor4_satisficing_heatmap.png`. |
| `plots/a08_actor4_regret_cdf.png` | `plots/final_project/a08_actor4_regret_cdf.png` | Replace with `plots/final_project/a08_actor4_regret_cdf.png`. |
