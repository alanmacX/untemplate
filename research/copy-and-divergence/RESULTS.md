# v12: copy as an acceptance gate, uncertainty as a search input

[Protocol](PROTOCOL.md) · [Chinese briefs](cases.json) · [Rendered DOM, replays and font measurements](evidence/browser.json) · [Copy review](evidence/copy-review.json) · [27 concept outputs](evidence/routes/) · [Deletion proof](evidence/repair.json)

## The handoff loses constraints; a stronger prompt still needs a check

The previous B/V builds passed their functional checks with a shared handoff saying to avoid boilerplate, but the implementation still added “Tool loans”, “Choose a task”, “Loan terms” and “Orchard map.” No browser check asked whether those slots added enough information. V12 puts that rule in the implementation prompt and in the acceptance procedure, separately from creative exploration. Review the semantic work of the words, including prefixes and helper text in empty or result states; check actual HTML, pseudo-elements and screenshots.

New Chinese holdout: same three briefs and generator (GPT-6.2 Sol). Each arm yields three pages; mobile and desktop are two views of the same page.

| Left to right in the screenshots | Pages with a removable phrase | Functional replays |
| --- | ---: | ---: |
| A: no skill | 2/3 | 6/6 |
| B: full v11 entrypoint as text | 3/3 | 6/6 |
| C: same entrypoint plus explicit copy gate in prompt | 2/3 | 6/6 |

Counts reflect conservative manual coding and should not be read as a difference in rates. The C radio page still said “先选收音机的现象，看看需要怎么检查” directly above the symptom control; the C book page told people to click titles to reveal location and time immediately before the list. The deadline, graphic labels, mock-mode notice and closure reason all matter. The independent deletion pass removed the two C phrases and repaired two earlier English fixtures (lab and orchard). **8/8** desktop and phone checks caught the original phrase, cleared it from the DOM after repair, and replayed the task without breaking the retained heading or its accessible reference.

Repaired phone comparisons, before on the left and after on the right: [radio](screens/radio-C-phone-copy-repair.jpg) · [book pickup](screens/books-C-phone-copy-repair.jpg) · [lab](screens/lab-loan-B-phone-copy-repair.jpg) · [orchard](screens/orchard-V-phone-copy-repair.jpg).

| Page | Desktop | Phone |
| --- | --- | --- |
| Radio repair | [A/B/C](screens/radio-desktop-first-ABC.jpg) | [A/B/C](screens/radio-phone-first-ABC.jpg) |
| Children's book pickup | [A/B/C](screens/books-desktop-first-ABC.jpg) | [A/B/C](screens/books-phone-first-ABC.jpg) |
| Riverside detour | [A/B/C](screens/trail-desktop-first-ABC.jpg) | [A/B/C](screens/trail-phone-first-ABC.jpg) |

## Why the route drifts back, and where to put uncertainty

1. **Variety at a low level leaves the preferred high-level branch intact.** Bare seeds give a different text token, while the model can still interpret the prompt via the same typical user and screen. [Wenger and Kenett's 22-model study](https://pmc.ncbi.nlm.nih.gov/articles/PMC13010328/) observes less population diversity than humans on three verbal idea tasks. [Design Creativity Bench](https://arxiv.org/html/2610.11539v2#S3) shows the corresponding failure on fixed goals and changing product content. Those findings measure outputs, not hidden layers in this test.
2. **A useful starting point and a separate search are two levers.** [Deng, Brucks and Toubia](https://arxiv.org/html/2602.20408v2) separate across-session anchoring to similar knowledge from within-session fixation in product ideation. Their interventions and conditions differ from UI. [Luo et al.](https://arxiv.org/html/2603.19519v2#S3) insert meaningful semantic stimuli in text generation at selected points; our treatment stays outside the decoder. Use a fresh start without the first draft. Draw a real fact or an outside activity's relation, then test whether it changes one still-open design decision. Keep accuracy, accessibility, and the copy gate fixed.
3. **The brief can fix the main action, and implementation can normalize everything else.** Test how the material, first glance or result relation can change rather than demanding a different button. Handoff the concrete relation before HTML and look at the actual pixels and states. Keep a useful alternative over an artificially different one.

The paired experiment holds facts and required features fixed. Each cell below is the number of distinct **primary mobile entry framings** judged from the visible contents and outcome in three requests. Labels describe actual proposals; the prompts did not give any categories. The expected control remains fixed by the brief. This descriptive hand-coding measures framing, not aesthetic creativity.

| Seed condition | Radio repair | Book pickup | Riverside detour |
| --- | --- | --- | --- |
| Number only | 1: symptom entry | 1: book-first | 1: detour status + slope |
| Draw an existing fact | 3: symptom, access/deadline, or consent terms | 1: book-first | 1: detour status + slope |
| Draw a fact plus outside relationship (exploratory) | 2: symptom or access/deadline | 2: group by book or pickup point | 1: detour status + slope |

Taking an outside relation led one book proposal to group titles under the North Gate pickup shelf and service desk, leaving title selection intact. The trail remained tied to the one safe route; one analogy replaced the initial map emphasis with a short route chain without changing the route or result. The radio dropped its consent-first opening in the exploratory analogy arm. When the seed fails to change an observable decision, try another premise, or preserve the useful route and explore detail, typography or material.

## Chinese type has its own template risk

In the nine actual pages, **7/9** headings rendered in Songti SC and **2/9** in PingFang SC on this Chrome/macOS stack. The headings were 58.4–86.4 CSS px on desktop; 4/9 used negative tracking. The recurring combination of a cream background, oversized heading and small instructional line survived different tasks and copy instructions. Typography has an independent acceptance check in v12.

In the fixed Chinese specimen, the CSS declaration starting with Georgia rendered **all 12 Chinese headline glyphs in Songti SC** on this machine; a locally specified Hei stack actually rendered PingFang SC. All three examples fit at 320px in this geometry check. That result does not measure how people read; it illustrates the need to look beyond the font declaration. [W3C CLReq](https://www.w3.org/TR/clreq/) describes regional glyph and punctuation conventions. [Dobres et al.](https://jdobr.es/pdf/Dobres-etal-2016-Displays.pdf) tested five Simplified Chinese faces in fast glance conditions; their evidence motivates checking strokes, weight and contrast for brief scanning, rather than choosing one face for every setting.

Use the text the page will carry: long heading, dense labels, units and numerals, and a real control with its result. On a narrow viewport compare weights, actual faces and fallback, line height, wrapping, whether information remains grouped, and whether the type suits the material. Choose regional language tags, check punctuation breaks, and judge both reading and visual expression.

## Reproduce

With existing Chrome, Python, Playwright and Pillow, from this directory:

```sh
python audit_browser.py evidence/pages /tmp/untemplate-v12-browser
python repair_probe.py evidence/pages /tmp/untemplate-v12-repaired
python specimen_fonts.py /tmp/untemplate-v12-fonts
```

To regenerate synthetic artifacts rather than replay them:

```sh
python run.py pages /tmp/untemplate-v12-pages
python run.py routes /tmp/untemplate-v12-routes
python run.py routes /tmp/untemplate-v12-routes --analogy
```
