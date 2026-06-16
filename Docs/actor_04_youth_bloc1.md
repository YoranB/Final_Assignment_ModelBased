# Actor 4 — Global Youth & Future Generations Coalition
## Bloc 1 — Existential Frontline

> **Keep this document private.** Your mandate describes who you are and what you want from the agreement. You may tell other groups what you want — you may not show them this document.

**Who you are:** You are a global coalition of youth movements. You carry significant moral authority in the room. You represent everyone who will live with the consequences for the next fifty years — and everyone not yet born.

**What you want:**
- 1.5°C is your floor
- The discount rate — how much less economists value future welfare compared to present welfare — is a political choice about intergenerational fairness, not a scientific fact. Challenge any actor who relies on high-discount results without disclosing this
- Carbon capture technology (CCS) and carbon trading schemes buy time, not safety — they are not substitutes for cutting emissions now
- You can be disruptive — call actors out by name when they contradict their stated positions
- **Red line:** Any text that removes 1.5°C as the operative target
- **Minimum condition:** An explicit commitment to near-zero social discount rate in the welfare accounting used to evaluate compliance

**Your welfare lens:** Your central argument is not about which welfare function to use — it is about how much the future counts. The parameter `pure_rate_of_social_time_preference` encodes a normative assumption about intergenerational equity. To compare two discount rates, use `PRIORITARIAN` (which defaults to ρ ≈ 0.0) as your low-discount run and `UTILITARIAN` (which defaults to ρ ≈ 0.015) as your high-discount comparison — these are the closest readily available contrast within the model's default configuration, but you are encouraged to go beyond these comparisons. The shift between the two Pareto fronts is your evidence.

*(Regions likely relevant to your case: `rjan57`, `rsas`.)*

**Some analytical directions to consider:**
1. How does your preferred Pareto solution shift between a near-zero and a standard economic discount rate? Which actors' proposals look better under high discounting — and what does that reveal?
2. How does `fraction_of_ensemble_above_threshold` compare between your low-ρ and high-ρ runs — at 2°C? If 1.5°C is not achievable under either discount rate, what does that reveal about the state of the negotiation — and whose preferred policies benefit from that gap?
3. If you show the Pareto fronts under both discount rates on the same plot, what does the shift reveal about whose welfare each rate prioritises?

**Sources:**
- [UNFCCC: "Climate Action Demands Intergenerational Solidarity"](https://unfccc.int/news/climate-action-demands-intergenerational-solidarity)
- [UNFCCC Youth-led Climate Forum: "Defending Intergenerational Equity in Just Transition and Climate Finance"](https://unfccc.int/event/youth-led-climate-forum-part-i-defending-intergenerational-equity-in-just-transition-climate-finance)
- [Carbon Brief: Today's youth will face "unmatched" climate extremes compared to older generations](https://www.carbonbrief.org/todays-youth-will-face-unmatched-climate-extremes-compared-to-older-generations/)
- [YOUNGO — Official Youth Constituency at UNFCCC](https://unfccc.int/topics/action-for-climate-empowerment-children-and-youth/youth/youngo)

> **Note for students:** The discount rate argument is grounded in academic economics, not a YOUNGO policy statement. Cite the Stern Review (2006) for the low-discount case and Nordhaus (2008) for the high-discount case — the debate between them is your primary evidence.
