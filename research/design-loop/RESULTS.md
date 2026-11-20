# A design instinct based on seeing and revising

[Briefs](cases.json) · [Frozen pages](evidence/pages/) · [Browser checks and measured line breaks](evidence/audit.json) · [v14 skill](../../skills/anti-aidesign/SKILL.md)

## Why this loop

Schön and Wiggins distinguish seeing literal marks, seeing relationships among them, and judging what has happened in the drawing. This informs an explicit feedback loop: use real material, make a version, see what entered the frame, then decide what to change. [Kinds of seeing and their functions in designing](https://www.sciencedirect.com/science/article/pii/0142694X9290268F).

Suwa and Tversky found that experienced designers see broader relationships and functions in sketches. In related work, designers could discover something they had not planned by reinterpreting a sketch. A prototype is therefore useful as evidence during design, not only as a presentation of a finished answer. [What architects see in their sketches](https://chi1996.acm.org/proceedings/shortpap/Suwa/sm_txt.html) · [Unexpected discoveries](https://www.johngero.com/publications/2000/SuwaGeroPurcellDesStu.pdf).

For visual judgment, [Hekkert's synthesis](https://pure.tudelft.nl/ws/portalfiles/portal/54686438/Hekkert_P._Design_aesthetics_principles_of_pleasure_in_design.pdf) discusses unity in variety and familiar forms with room for novelty. These are ways to notice competing qualities, not a digital taste score. [Andy Clarke's account of art direction](https://www.smashingmagazine.com/2019/11/smashing-podcast-episode-1/) links layout, type and color to the impression available to a viewer. In [Cameron's World](https://www.cameronsworld.net/), the actual heterogeneous GeoCities material determines the density and wandering rhythm. [Endless Horse](https://secure.endless.horse/) is a visual joke, organized around its own absurd duration, as [its authors describe](https://theuselessweb.com/sites/endless-horse/). Our browser opened both; the Cameron page was also scrolled. Neither needs a conversion objective.

For an agent, the habit is: **notice an actual viewing moment, choose a visible relationship, look at real output, change a concrete decision**. The things to look for are emphasis, scale and distance, pacing, treatment of the material and what holds the parts together. The relative importance depends on the piece. A still screen can meet the brief. A redesign starts by specifying what is already worth keeping; it need not flatten that identity while removing boilerplate.

## Test design

Same model, GPT-6.2 Sol. Two briefs: a new expressive piece with no business function (Tide Line), and a research copy of an existing working art display (Watercolors). Same text, assets and functional constraints in each case. A and B both receive the same original HTML and desktop/phone captures when redesigning.

- **A:** full v13 entry point as text with the brief. This is a skill baseline.
- **B:** same entry point and brief plus the v14 perceptual/art-direction prompt in run.py.
- **C:** same B page after one visual review. A fresh request receives B's actual desktop and mobile Chrome screenshots, the B HTML and the original brief. It returns at most two concrete edits and revised HTML. Tide Line's first image request timed out; a retry used compressed copies of the same two screenshots.

These are two observed trajectories, not a blinded taste study or an estimate of the benefit of additional inference effort. We compare what the second look actually changed.

## Browser results

Six outputs plus the preserved original, on desktop (1440px), phone (390px) and narrow (320px): **21/21** checks passed. For Tide Line the browser verifies the title and four lines verbatim, in visual order, with no clipping caused by horizontal overflow. For Watercolors it checks real loaded images, initial side-by-side display, both record selections, archive names and IDs, and visible source. On the tested phone viewport all four watercolors variants kept both full sheets visible in the first screen.

| Case | What the treatment actually did | Screenshots |
| --- | --- | --- |
| Tide Line | A stretched the phone piece over 2,566px and let one line arrive at a time. B fit the whole piece in 844px with a final pause; all three versions used no visible controls. Review found that B stranded only the final fragment “上窗。” on its second line and let a bright stair edge cross the text. C breaks at the comma, keeps the closing-window phrase together and dims the edge under the words; it keeps the single-screen approach. A's slower cadence remains a viable aesthetic decision. | [Phone A/B/C](screens/tide-phone-first-A-B-C.jpg) · [Desktop A/B/C](screens/tide-desktop-first-A-B-C.jpg) |
| Watercolors | B keeps both sheets at full scale and removes the red editorial trim around them. C notices the remaining boxed archive control interrupts the sequence from picture to caption. A thin underline replaces the box; the button retains its measured 44px height, and both records still switch. On the phone the first image begins at 134px in B/C and 161px in the original. | [Phone original/C](screens/plates-phone-first-original-C.jpg) · [Phone B/C](screens/plates-phone-first-B-C.jpg) · [Archive state](screens/plates-phone-end-original-C.jpg) |

The review found changes specifically in a mark, a line and a relationship. The workflow is useful when the first draft already functions or when the entire piece is an aesthetic experience. It does not ask the user to justify the work as a product. No blanket style rule was added.

## Reproduce

With Python, Pillow, Playwright and an existing Chrome, from this directory:

```sh
python check.py evidence/pages /tmp/untemplate-design-loop
```

To regenerate through the same Codex model, run python run.py with an output directory. To replay only a visual pass for a previously generated case, supply --feedback-only and its case ID. No screenshots of third-party sites are republished.
