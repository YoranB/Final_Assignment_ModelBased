# Actor Mandates to JUSTICE Guide

This page contains the shared reference material that applies to **all actors** regardless of which bloc they represent.

---

## Part 1: JUSTICE Model Reference

### 1.1 Your mandate is not directly translatable to JUSTICE

JUSTICE has no one to one mapping to your mandate.  You must construct proxies. Examples:

- Arguing for **ambitious mitigation in high-emission regions** → compare `emissions` and `damage_fraction` for coal-dependent regions (`pol`, `zaf`, `chn`, `rus`) across Pareto solutions
- Arguing that **poor regions should not bear equal abatement burden** → compare `abatement_cost / gross_economic_output` across regions at the same Pareto solution


### 1.2 What the model can give you

| Output variable | What it means | Unit |
|---|---|---|
| `global_temperature` | Global mean temperature above pre-industrial | °C |
| `regional_temperature` | Temperature per region | °C |
| `gross_economic_output` | Total economic output before damages and abatement | Trill 2005 USD PPP/yr |
| `net_economic_output` | Economic output after damages and abatement costs | Trill 2005 USD PPP/yr |
| `damage_fraction` | Share of GDP lost to climate damages, per region | dimensionless |
| `economic_damage` | Total monetary damages per region | Trill 2005 USD PPP/yr |
| `damage_cost_per_capita` | Climate damages per person per region | k USD/capita/yr |
| `abatement_cost` | Total abatement cost per region | Trill 2005 USD PPP/yr |
| `abatement_cost_per_capita` | Cost of emission cuts per person per region | k USD/capita/yr |
| `consumption_per_capita` | Net consumption per person per region | k USD/capita/yr |
| `emissions` | CO₂ emissions per region | GtCO₂/yr |
| `welfare` | Single aggregate welfare scalar for the entire model run | dimensionless |
| `spatially_disaggregated_welfare` | Welfare broken down per region — requires a separate computation step, not a `model.data` key | dimensionless |
| `fraction_of_ensemble_above_threshold` | Fraction of climate ensemble members (or climate states of the world) exceeding a temperature threshold at a given year — requires a separate function call, not a `model.data` key | 0–1 |

**Key analytical ratios:**
- `abatement_cost / gross_economic_output` — abatement burden as share of GDP, comparable across regions
- `economic_damage / gross_economic_output` — equivalent to `damage_fraction`

> `model.data` already contains `consumption_per_capita`, `damage_cost_per_capita`, and `abatement_cost_per_capita` — these require no extra steps. For anything else per-capita (e.g. per-capita `emissions`), population is not in `model.data`; retrieve it via `model.economy.get_population()` and divide: `model.data["emissions"] / model.economy.get_population()`.

### 1.3 Region codes

| Code | Region | Code | Region |
|---|---|---|---|
| `arg` | Argentina | `aus` | Australia |
| `aut` | Austria | `bel` | Belgium |
| `bgr` | Bulgaria | `blt` | Baltic States |
| `bra` | Brazil | `can` | Canada |
| `chl` | Chile | `chn` | China |
| `cor` | South Korea | `cro` | Croatia |
| `dnk` | Denmark | `egy` | Egypt |
| `esp` | Spain | `fin` | Finland |
| `fra` | France | `gbr` | United Kingdom |
| `golf57` | Gulf Countries | `grc` | Greece |
| `hun` | Hungary | `idn` | Indonesia |
| `irl` | Ireland | `ita` | Italy |
| `jpn` | Japan | `meme` | Middle East |
| `mex` | Mexico | `mys` | Malaysia |
| `nde` | India | `nld` | Netherlands |
| `noan` | W. Sahara, Tunisia & Morocco | `noap` | Libya & Algeria |
| `nor` | Norway | `oeu` | Other European Countries (incl. Iceland) |
| `osea` | Rest of Southeast Asia | `pol` | Poland |
| `prt` | Portugal | `rcam` | Rest of Central America & Caribbean |
| `rcz` | Czechia | `rfa` | Germany |
| `ris` | Former Soviet Union | `rjan57` | Pacific Islands |
| `rom` | Romania | `rsaf` | Sub-Saharan Africa |
| `rsam` | Rest of South America | `rsas` | Rest of South Asia |
| `rsl` | Slovakia | `rus` | Russia |
| `slo` | Slovenia | `sui` | Switzerland |
| `swe` | Sweden | `tha` | Thailand |
| `tur` | Turkey | `ukr` | Ukraine |
| `usa` | United States | `vnm` | Vietnam |
| `zaf` | South Africa | | |

### 1.4 Welfare functions — what each one asks

Your mandate describes a normative principle. You must identify which function best captures it.

| Function | The normative principle |
|---|---|
| `UTILITARIAN` | Maximise total welfare across all regions, treating every unit equally regardless of who receives it |
| `PRIORITARIAN` | Give extra weight to the worst-off regions — a welfare gain for the most exposed matters more than an equal gain for the best-off |
| `SUFFICIENTARIAN` | Treat falling below a basic minimum (~$0.456k/capita/yr, equivalent to $1.25/day in 2005 PPP) as the first priority before any aggregate calculation |
| `EGALITARIAN` | Penalise the gap between the best-off and worst-off regions — narrowing the gap matters even at some cost to the global total |

---

## Part 2: Universal Workflow

1. **Translate** your mandate into model terms: identify your welfare function, key regions, key variables, and satisficing criterion — the minimum acceptable outcome you define for your actor.
2. **Optimise** — run the MOEA under your chosen welfare function and reference scenario (you can modify the normative parameters for each welfare function, e.g. the risk aversion, inequality aversion, pure rate of time preference, egality strictness, and sufficiency threshold). The output is a Pareto archive.
3. **Re-evaluate** your preferred solution to extract full variable time series across the simulation horizon.
4. **Test robustness** — re-evaluate across multiple SSP scenarios and ensemble members; compute the fraction of runs where your criterion is met.
5. **Run the rival framing** — re-optimise under the rival welfare function; compare the two Pareto fronts. This step is strongly recommended for all actors. If compute time is limited, at minimum compare your preferred Pareto solution's outcomes under the rival welfare function without re-optimising.

### How to read your mandate

The regions, variables, and analytical directions in your mandate are a suggested starting point. You are welcome to use different variables, additional regions, or a different analytical angle. You are encouraged to go further if you find something more compelling.

**Political demands vs model evidence.** Every actor in this negotiation will use two types of argument:

- **Model-based arguments** — claims you can back with JUSTICE output: a number, a comparison across regions, a robustness metric, a welfare value.
- **Political arguments** — claims grounded in values, historical responsibility, legal precedent, or fairness principles that JUSTICE does not compute. A Loss and Damage fund, a Just Transition mechanism, carbon market rules, carbon capture storage (CCS) recognition, none of these have a direct JUSTICE equivalent. They are still legitimate in a debate. For these arguments, support your position with evidence from credible sources, IPCC reports, UNFCCC decisions, peer-reviewed research, or official national statements.


---

## Part 3: Debate Evidence Card

This is a suggested evidence card that your group can bring to have an accessible in-debate reference.

| Field | Your entry |
|---|---|
| **Actor** | |
| **Welfare function chosen** | |
| **Why this function fits your mandate** |  |
| **Key region(s)** | |
| **Key output(s) to cite** | |
| **Preferred Pareto solution** |  |
| **Satisficing criterion** | |
| **Robustness score** | |
| **Rival welfare function** | |
| **What the rival framing shows** |  |
| **Your absolute red line** | |
| **Your minimum condition for yes** | |
| **One political argument you will make** | |
