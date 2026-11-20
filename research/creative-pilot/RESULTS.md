# Creative pilot: opening the search, keeping the result

[Protocol](PROTOCOL.md) · [Cases](cases.json) · [Prompts](prompts.json) · [Anonymous-pair verdicts](evidence/review-joint.json) · [Typography measurements](evidence/type.json) · [Browser replays](evidence/browser.json)

## What generalizes

An under-specified brief leaves many valid designs. A text-generating model gives these designs uneven probability; once a familiar premise and page outline have been written, later decisions are conditioned on them. Many different phrases, fonts and values can still implement the same page. The hosting product also supplies its own prompts, starter code, tools, and selection loop. The evidence supports studying those stages separately; it does not identify which closed model weights caused a particular visual default.

- **Cross-family tendency, checkpoint-dependent behavior.** [Wenger and Kenett](https://pmc.ncbi.nlm.nih.gov/articles/PMC13010328/) compared 22 LLMs with 102 people on verbal divergent-thinking tasks. Across the tasks, model responses were less varied as a population. [Design Creativity Bench](https://arxiv.org/html/2610.11539v2#S3) measures a different task: 15 models generated frontend designs with a fixed archetype and goal but changing industry and sample content. Mean distinctiveness was 0.581, versus 0.902 for the human reference. [Sclar et al.](https://proceedings.iclr.cc/paper_files/paper/2024/hash/6c0e99d736da621403018ca7b32b1a4d-Abstract-Conference.html) found that the impact of formatting choices in few-shot tasks correlates weakly across some model pairs. None of these establishes a universal gain from a particular prompt. Treat every release, product wrapper, and benchmark setting as an experimental condition.
- **Search a different problem, then explore a solution.** In [Dorst and Cross's protocol study](https://doi.org/10.1016/S0142-694X(01)00009-6), nine experienced industrial designers changed their understanding of the task as they developed solutions. [Beaty and Silvia](https://pure.psu.edu/en/publications/why-do-ideas-get-more-creative-across-time-an-executive-interpret/) found that later ideas can improve through strategic retrieval; simply moving further from the prompt is a poor specification for that process. Ask what someone knows, has or needs to decide, and let the actual content invalidate a premature assumption.
- **Transfer a mechanism, with a place to fail.** In human experiments, [Gick and Holyoak](https://reasoninglab.psych.ucla.edu/wp-content/uploads/sites/273/2021/04/Gick_Holyoak1983_SchemaInduction.pdf) and [Gentner et al.](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf) found evidence that comparing concrete cases can help people abstract a relation they transfer to a new task. Use it as an optional way to search. The borrowed mechanism should change a decision for this user without creating a new business rule.
- **Use outside information and stopping rules.** [Dow et al.'s parallel prototyping study](https://hci.stanford.edu/publications/2010/parallel-prototyping/ParallelPrototyping2010-final.pdf) supports starting separate alternatives before committing to the first one. In an agent workflow, use real project facts, useful references and artifacts to steer alternate starts. Optional external seed allocation only distributes the search budget. Grounding, semantics and interaction tests decide what can ship. Look at an equivalent-fidelity desktop/mobile pair to decide whether the difference is visible.

## Measured concept effects

Two GPT checkpoints × six briefs × three conditions = 36 fresh requests, 72 short concepts. The judge (GPT-6.2 Sol) saw shuffled pairs with condition and source labels removed; familiar phrasing inside some sketches can still hint at the intervention. The table reports the joint pass, with each passing pair both usable and consequentially different. This is a model-assisted content audit; it records no human judgments of creative quality.

| Checkpoint | A ground | B change a premise | C change a premise + cross-domain transfer |
| --- | ---: | ---: | ---: |
| GPT-6.2 Sol | 4/6 | 5/6 | 5/6 |
| GPT-5.6 Sol | 4/6 | 4/6 | 4/6 |

For 6.2 Sol, B separated actual fit comparison from date-first eligibility in the costume problem; A proposed two visual treatments that carried people through the same date-first action. In the walk, asking about the choir cutoff led a proposal to imply a connection to a particular crossing that the available facts do not establish. In 5.6 Sol, C's costume variant made an optional alteration slot a loan prerequisite. Search should fail closed on new restrictions and relationships. In the earlier separate pass over only GPT-6.2 outputs, B scored 6/6 instead of 5/6, and C 5/6 in both passes. The soundwalk ambiguity shows why borderline items and the separate adequacy gate are useful.

The measured effect differs even across these two checkpoints. The practical change adopted in v11 is a conditional search move when sketches converge. Analogical transfer remains optional. The protocol includes an adapter to run the same cases on another provider, and does not require downloading weights.

## Carry a real relation to implementation

Six preview pages at 1440 × 1000 and 390 × 844, **12/12** functional replays passed. A/B used the same implementation prompt. On the orchard page, what users could do differed (booking button vs. click an available row), but the heading, cream surface and earthy green accents remained close. In V, the same B route got a separate visual handoff: the row controls, closure and heading occupy the same map surface; confirmation follows it ahead of the shop note. In the lab, the task choices and result sit on one working surface rather than below a decorative cover.

| Starting position at 390px | B | V |
| --- | ---: | ---: |
| Lab: first task control top | 296px | 162px |
| Orchard: open-row controls top | 602px | 298px |

- Lab: [desktop A/B](screens/lab-loan-desktop-first-AB.jpg) · [phone A/B](screens/lab-loan-phone-first-AB.jpg) · [desktop B/V](screens/lab-loan-desktop-first-BV.jpg) · [phone B/V](screens/lab-loan-phone-first-BV.jpg) · [phone result B/V](screens/lab-loan-phone-result-BV.jpg)
- Orchard: [desktop A/B](screens/orchard-desktop-first-AB.jpg) · [phone A/B](screens/orchard-phone-first-AB.jpg) · [desktop B/V](screens/orchard-desktop-first-BV.jpg) · [phone B/V](screens/orchard-phone-first-BV.jpg) · [phone result B/V](screens/orchard-phone-result-BV.jpg)

V is exploratory and changes more than one visual variable. The screenshots document actual placement, display and task behavior without claiming aesthetic wins. All generated prototypes are frozen in [fixtures](fixtures/); each uses synthetic service data.

## Typography is a separate decision

Chrome's reported rendered faces: five of six headings used Georgia; the sixth used the macOS system face. All six had tightly negative tracking on desktop (−3.96 to −7.14px). The three orchard headings remained Georgia, including after the matched visual handoff; desktop sizes were 82.8px, 87.84px and 75.6px, respectively. The measured group is two briefs and multiple implementations, rather than six independent industries. All six had no document-level horizontal overflow at 320px in the original and spacing-stress passes; this measured geometry, not a full WCAG audit or reading study.

The result is consistent with the independently observed archetype at one site-building service. In [One Tool, One Taste? Appendix A.7](https://arxiv.org/html/2609.38183v1#A1.SS7), among 72 pages with extracted font values, Playfair Display (24) and Cormorant Garamond (12) dominate named headlines; Inter (36) is common in body copy. A suitable common face is useful. The repeating combination of huge title, tight tracking, display/body split and tiny uppercase may still overwhelm information that ought to lead. [IBM Carbon](https://www.carbondesignsystem.com/building-blocks/foundations/typography/style-strategies) separates productive and expressive roles. [Wallace et al.](https://www.bendsawyer.com/wp-content/uploads/2025/05/Wallace-et-al_2022_Toward-Individuated-Reading-Experiences.pdf) measured 352 readers with English passages and found that the best-performing font varied by reader.

The skill now asks for a real long headline, a condition or record, and a real action in the same comparison. Evaluate actual faces and fallback, width, weight, spacing and where text wraps. Compare what becomes easy to spot or stay with. Use the language and numerals used by the actual task; [W3C Chinese layout](https://www.w3.org/TR/clreq/) and [text-spacing override guidance](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) cover concrete checks.

## Reproduce

From this directory, run with Python 3.10+ and an existing backend:

```sh
python run.py --model gpt-6.2-sol --label gpt --out /tmp/untemplate-concepts
python run.py --api https://YOUR-CHAT-ENDPOINT/v1 --model YOUR-MODEL --label your-backend --out /tmp/untemplate-concepts
python score.py --in-dir /tmp/untemplate-concepts --out /tmp/untemplate-review.json
```

The Chat Completions adapter reads Bearer credentials from `UNTEMPLATE_CHAT_API_KEY` if needed; use `--omit-seed` for endpoints without seed support. `score.py` is optional; a human can review anonymized pairs using the same protocol. To reproduce the screen and type audits, install Playwright and Pillow, use an existing Chrome, and run:

```sh
python browser_check.py fixtures /tmp/untemplate-screens --visual
python type_audit.py fixtures /tmp/untemplate-type.json
```

For subsequent releases, keep the fixtures and constraints fixed; include a paraphrased brief and more than one provider with per-checkpoint results. Record a difference as useful only if it survives the task test and the full composition. Publish disagreements and failures alongside gains.
