# Human craft probe: start with the thing, pass the trade-off into the build

[Reference walk record](evidence/reference-audit.json) · [Two briefs with fixed materials](cases.json) · [Frozen implementations and concept drafts](evidence/pages/) · [Browser and geometry measurements](evidence/audit.json)

## What we looked at

Public pages sampled deliberately for different jobs, not as a statistical model-vs-human benchmark. Screenshots captured at 1440×1000 and 390×844. Published work records establish design provenance where available; for daily services the page is evidence of how the running service works, not a claim about every tool used to build it.

| Reference | A choice grounded in the work it handles |
| --- | --- |
| [The Creative Independent](https://thecreativeindependent.com/) · [author's process](https://laurelschwulst.com/e/tci-website/) | The bold color rectangles are current published records. A visitor can filter to interviews and open one; the interview is divided into an introduction/portrait, the conversation and related information. Laurel Schwulst starts at the interview as the core unit. Bold palettes, box borders, a mascot and playful type coexist with working editorial architecture. |
| [The Serving Library](https://www.servinglibrary.org/) · [project provenance](https://artistsspace.org/exhibitions/the-serving-library-2/) | The initial page groups heterogeneous visual records and captions without forcing all records into identical framed panels. The collection link opens an index of specific objects, and the captions identify actual work. A tight utilitarian label can belong in this system. |
| [Broomwagon Services](https://broomwagonbikes.com/services/) | Real storefront signage and actual workshop photographs give the colored cover a specific place. The service page explains the need to see the bike before quoting and leads into mobile repair. On the phone the photographic cover also delays access to those service rules; it is a trade-off, not a mandatory pattern to borrow. |
| [Edinburgh Tool Library inventory](https://edinburgh.myturn.com/library/inventory/browse) | Uses an ordinary vendor inventory template. The item-specific photographs, due dates and locations do the work. Filtering by location and availability matters more to that task than an expressive hero. |
| [justfont's 金萱](https://justfont.com/jinxuan/) | The mobile view enlarges real characters at different weights and lets you see the strokes, then uses text in a normal reading size. The type is the exhibit. A generic giant title would not do the same job. |
| [TXTbooks](https://www.txtbooks.us/) · [publisher's notes](https://www.txtbooks.us/info/) | Bright printed register and the publisher's type are visible; shipping information and publications give them a specific context. Opening the product through the homepage overlay did not complete in this run. |
| [Radio Garden](https://radio.garden/) · [authors' design account](https://studiomoniker.com/projects/radio-garden) | The project organizes listening by moving across places. The author record explains the interaction. Browser capture reached the start overlay; streaming was not verified. |
| [WANGZHIHONG CO.](https://wangzhihong.com/) | Home and Work navigation captured. The work image asset did not render in this environment; no conclusion based on that artwork's size or color. A site blocked by a certificate error (Bicycle Box) was excluded from visual comparison. |

The failure we care about is treating the expected appearance of a finished site as the first deliverable. Then the project contributes nouns and ornaments: film suggests a perforation, old paintings suggest paper and a display serif. Useful visual character can also come from a decision about the actual thing. Showing two cuts together and making one set of hand-written notes readable are competing jobs: their relative scale and reading sequence should be chosen before a decorative register. A standard component can be the right choice in such a design. Ordinary and expressive are different tools; both can be intentional.

## Two fresh briefs, four passes

Fixed synthetic film pickup records and two real, public-domain archival watercolors. All conditions receive the identical brief, facts, artwork and interaction contract. No previously generated site is passed as a starting body.

- **A, v12 entrypoint:** no separate reference observations. This is a skill baseline; it is not a no-skill run.
- **B, short reference observations:** the same entrypoint plus observations framed as short text, not the full screenshots or site. The author statements were used as prompts, not ground-truth grading.
- **C, material-first:** same inputs as B, with a separate model call to lay out one working object, actual text/images and the two states. It compares two arrangements and chooses one; that draft is passed into the same implementation interface.
- **D, discarded choice:** later test; give precisely the same C draft and ask to build the other, viable choice instead of the one selected. Same model endpoint. Because C and D use extra stages and D was exploratory, comparisons are probes of where change can happen, not effect sizes for a fully controlled benchmark.

| Task | Mobile opening A / B / C | What D changes |
| --- | --- | --- |
| Film pickup | First actual receipt controls at **151 / 289 / 111px**. Reference-only B added a dark imitation film strip and a jump link before the work; C puts the receipt above the route note and pairs each time with its corresponding place. | The two pickup places keep their own areas; selecting a record changes the matching area, rather than changing the whole receipt in one slot. Pickup instructions stay at their corresponding area. |
| Two watercolors | All keep both originals. B puts the choice panel after the images on mobile. C places the two choices above equal-width images that start at the same height and keeps the opened archive stable. | The first plate is **358px vs. 169px** wide on phone; the second starts at **749px vs. 153px**. The whole sheet and handwriting become larger; one-glance comparison is sacrificed and both originals remain available. |

**16/16** desktop/phone functional replays passed. The first loop checked both receipt variants, deadlines and access; the second checked both archival labels and the two image loads. All eight rendered page bodies still chose a warm light background, including both discarded directions. Two plausible structures existed; selecting an alternative changed structure and scale, and did not by itself change the familiar finish. There is no new aesthetic preference win recorded here.

| | First screen ABC | Selected vs. discarded CD |
| --- | --- | --- |
| Film / desktop | [First](screens/film-desktop-first-ABC.jpg) | [Result](screens/film-desktop-result-CD.jpg) |
| Film / phone | [First](screens/film-phone-first-ABC.jpg) | [Result](screens/film-phone-result-CD.jpg) |
| Watercolors / desktop | [First](screens/plates-desktop-first-ABC.jpg) | [First](screens/plates-desktop-first-CD.jpg) |
| Watercolors / phone | [First](screens/plates-phone-first-ABC.jpg) | [First](screens/plates-phone-first-CD.jpg) |

## What changed in the skill

Render the working object and one change in state before finishing a generic website. Show two real trade-offs in the actual viewport before a prose-only selection can make the choice. The same slow-reading, glance, or viewing-distance constraint that determines scale can also function as the stance for typography and surface. Review those separately after structure: even a useful layout can preserve a default color and rhythm from the generator. The copy gate from v12 still applies.

Our inference: the early description of the object and the accepted draft constrain subsequent code; references which arrive as themes or feature lists can be treated as extra motifs. This is about what was visible in these outputs, not a test of a model's internal representations. [Dorst and Cross's nine expert designers](https://www.sciencedirect.com/science/article/pii/S0142694X01000096) revised the problem as their partial solutions evolved. Make that loop possible here by letting the materials and partial artifact change the question. [UI design diversity measurements](https://arxiv.org/html/2610.11539v2#S3) explain why just supplying another industry is a weak test for transferable creativity.

## Reproduce

From this directory with Python, Playwright, Pillow and an existing Chrome:

```sh
python check.py evidence/pages /tmp/untemplate-human-craft-screens
```

To regenerate, place the two credited images under the output directory's assets folder, run the same CLI model through run.py, then add the --alternate pass using its frozen C drafts. The public reference URLs are in the walk record; no third-party reference screenshots are republished in this repository.
