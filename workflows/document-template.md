# Document Template

Fill-in-the-blanks skeleton. Copy it, fill every `<...>` slot, delete slots
that do not apply. Section order is fixed; the numbered technical sections
scale to the session.

A section **must** carry at least one Figure (a diagram or plot) — the
audit gate enforces this — and may carry more than one (density favors a
second). It may not omit the other three parts.

````markdown
# <Project / Session Title>

## TL;DR

<3–6 sentences: what was built, the key result, the key decision. A reader
who stops here must be left with the correct picture.>

## Why This Matters

<The project-level stake: what was at risk or stuck before this session,
what this work unlocks, and who benefits. Not a section recap.>

## Background: What You Need to Know First

<Prerequisite concepts in dependency order. Each gets an in-line,
intuitive-voice definition at first use. This is the foundation the
technical sections build on — if a later section needs a concept that is
not here, it belongs here.>

- <Concept 1>. <one-sentence intuitive definition>.
- <Concept 2> (builds on Concept 1). <definition>.
- <Concept N>. <definition>.

## Section 1: <first technical component>

Why this matters: <2–4 sentences. What breaks without this? What does it
unlock? Specific to this section — no generic filler.>

**Intuitively.** <Everyday analogy or concrete scenario, zero unexplained
jargon. The reader should be able to predict what the technical pass says.>

**Technically.** <Rigorous version for a domain expert: equations,
complexity, parameter values, library versions, algorithm names,
citations. Do not dumb down.>

![Fig 1: <takeaway, not contents>](figures/fig-01-<slug>.png)

## Section 2: <next component>

Why this matters: <...>

**Intuitively.** <...>

**Technically.** <...>

![Fig 2: <takeaway>](figures/fig-02-<slug>.png)

<!-- Repeat as needed: Section N. -->

## Results

<What the work produced, with numbers/measurements where the session
produced them. Traceable claims — state provenance.>

## What's Next

<Concrete follow-ups, genuinely open questions, and known limitations.
Do not list zombie problems here — those belong in Appendix A.>

## Appendix A: Corrections and Dead Ends

<!-- Genuinely useful detours only. Trivial one-offs are omitted. If none,
     write "None." -->

### A.1 — <short name for the issue>

**What we observed:** <symptom, as seen>
**Root cause:** <actual cause, technically stated>
**Resolution:** <what fixed it>
**Generalizable lesson:** <what to watch for next time — or "none">

## Appendix B: Glossary

<!-- Alphabetized. Every in-line defined term appears here. If none,
     write "None." -->

**<Term>.** <one-sentence intuitive gloss>. — *Precisely:* <one-sentence
formal definition>.

## Appendix C: Reproducing the Figures

<!-- Full plotting script(s). Pin the XY version. One block per figure. -->

**XY version:** `<pin, e.g. 0.0.7>`

```python
# figures/fig-01-<slug>.png
import xy

# <one-line theme defined once, reused across all figures>
THEME = xy.theme(...)

chart = xy.line_chart(
    xy.line(x, y, color="#7c3aed", width=3),
    THEME,
    title="...",
)
chart.to_png("figures/fig-01-<slug>.png")
```
````

## Filling notes

- **TL;DR and Why This Matters are project-level.** They answer "what and
  why for the whole session", not per-section.
- **Background is a ladder.** Order it so each concept uses only concepts
  above it. A reader who reads Background alone should have every term the
  technical sections rely on.
- **Number figures in document order.** `fig-01`, `fig-02`, … The audit
  gate checks that every referenced figure file exists.
- **Appendix A is not a changelog.** It is a collection of lessons. A typo
  fix is not an entry. A subtle root-cause discovery is.
- **The three appendices are required headings** even when empty ("None.").
  Their presence is what makes the document navigable and honest.
