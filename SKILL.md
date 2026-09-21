---
name: technical-session-writeup
description: Produce a single Markdown write-up of a technical working session — what was built, what was learned, and why it mattered — that a brilliant non-specialist and a domain expert can both read and each get what they need. Use this skill when the user says "write this up", "summarize the session", "generate the write-up", "document what we did", "session recap", "handoff doc", or invokes it by name at the end of a technical conversation. Do NOT use it for quick answers, single-question exchanges, code comments, or docstrings.
---

# technical-session-writeup

Convert a technical working session into **one Markdown file** that documents
what was built, what was learned, and why it mattered — written for two
readers at once: a brilliant non-specialist and a domain expert.

## When to use

**Trigger** when any of these is true:

- The user says "write this up", "summarize the session", "generate the
  write-up", "document what we did", or invokes this skill by name.
- The user asks for a session summary, handoff doc, or project recap at the
  end of a technical conversation.

**Do NOT trigger** when:

- The exchange is a quick answer or a single question.
- The user wants a code comment, docstring, commit message, or inline note.
- There is no session to document (no technical work was done this
  conversation). If in doubt, ask.

## Purpose: the four problems this skill exists to solve

Every rule in this skill exists to correct one of these failure modes.
Write the document so that each of them is explicitly, verifiably fixed:

1. **Undefined jargon.** Technical write-ups use specialized terms and never
   define them, leaving the reader to guess. → Corrected by the *first-use
   inline definition* rule (Layering, below) and Appendix B.
2. **Zombie problems.** Write-ups resurrect failure modes, bugs, and dead
   ends that were diagnosed and fixed hours ago, presenting finished work as
   if it were still broken. → Corrected by the *corrections rule*: the main
   body reports only the final, correct state; every detour lives in
   Appendix A (below).
3. **Missing "why."** Write-ups describe *what* was done in exhaustive
   mechanical detail and never say why it was worth doing, what would have
   gone wrong otherwise, or what it unlocks. → Corrected by the mandatory
   "Why this matters" opening of every section (Section template, below).
4. **One-audience writing.** Write-ups pick a single altitude — hand-wavy or
   impenetrable — and fail the other audience entirely. → Corrected by the
   dual *Intuitively / Technically* passes in every section.

## Required document structure

Produce exactly this shape (section order is mandatory; the numbered
technical sections vary in count to match the session's components):

```
# <Project / Session Title>

## TL;DR
## Why This Matters
## Background: What You Need to Know First
## <Section 1: first technical component>
## <Section 2: ...>
## <Section N>
## Results
## What's Next
## Appendix A: Corrections and Dead Ends
## Appendix B: Glossary
## Appendix C: Reproducing the Figures
```

- **TL;DR** — 3–6 sentences. The whole story: what was built, the key
  result, the key decision. A busy reader who stops here should be correct.
- **Why This Matters** — the project-level "why": the stake, the cost of
  the status quo, what this work unlocks. Not a section-by-section recap.
- **Background: What You Need to Know First** — every prerequisite concept,
  laid down in dependency order before any technical section uses it. If a
  section needs a concept that hasn't been established, it belongs here,
  never as an inline aside.
- **Results** — what the work produced, with numbers/measurements where
  the session produced them. Traceable claims.
- **What's Next** — concrete follow-ups, open questions, and known
  limitations that are genuinely open (not zombie problems — see Appendix A).

## Per-section template (every technical section)

Each numbered `## <Section N>` must contain these parts, **in this order**:

1. **Why this matters** — 2–4 sentences. What breaks without this? What does
   it unlock? This must be *specific to the section* — never generic filler
   ("this is important because it improves performance" fails the audit).
2. **Intuitively** — the concept explained through an everyday analogy or
   concrete scenario, with **zero unexplained jargon**. A smart person
   outside the field must be able to follow this and *correctly predict*
   what the technical pass will say.
3. **Technically** — the rigorous version, aimed squarely at a domain
   expert: equations, complexity bounds, parameter values, library versions,
   algorithm names, citations. Do **not** dumb this down — the intuitive
   pass already did that job.
4. **Figure** — a diagram or plot, **where it genuinely clarifies**. Not
   decoration. If a figure would not teach the reader something the prose
   cannot, omit it and say so is fine; a forced figure is a defect.

**The intuitive and technical passes must describe the *same thing*.** A
common failure is the analogy drifting into a different concept than the one
being formalized. Before finalizing, verify both passes land in the same
place: the technical pass must be a formalization of the analogy, not a
replacement for it.

Label the passes with bold leads so the reader can scan by altitude:

```markdown
## Section 2: <name>

Why this matters: <2–4 sentences, specific>

**Intuitively.** <analogy / scenario, no unexplained jargon>

**Technically.** <rigorous: formulas, versions, bounds, citations>

![Fig N: <takeaway>](figures/fig-NN-<slug>.png)
<caption sentence if the image alt text is not the full takeaway>
```

## The layering rule ("ELI5 for a genius")

The reader is a five-year-old who happens to be the smartest person you have
ever met. They can absorb quantum field theory — but only if you build it.

- **Never use a term before defining it.** Not "we'll define this later",
  not "as is well known". First use gets an in-line definition, in the
  intuitive voice.
- **Build ladders, not walls.** Concept 3 should rest on concepts 1 and 2.
  If a section needs a prerequisite that hasn't been laid down, add it to
  "Background" rather than dropping it inline as an aside.
- **No condescension.** No "don't worry about the math", no "this is
  complicated but basically". The reader can handle it — your job is
  *ordering*, not omission.
- **Analogies must be load-bearing.** A good analogy lets the reader make a
  correct prediction about the system. If the analogy can't do that, it's
  ornamental — cut it.
- **One level deeper.** Assume the reader will ask "but why does *that*
  work?" one level deeper than you planned. Have the answer, and place it
  where that question naturally arises.

## The corrections rule (strictest requirement in this skill)

**The main body reports only the correct, final state of things.** If the
session tried approach A, found it wrong, and moved to approach B, the main
body documents B *as if B were the plan*. No "we initially thought", no
"after some debugging", no narration of the detour.

**All errors, corrections, reversals, and dead ends go in Appendix A.**
Nowhere else. Each entry:

```markdown
### A.N — <short name for the issue>

**What we observed:** <symptom, as seen>
**Root cause:** <the actual cause, technically stated>
**Resolution:** <what fixed it>
**Generalizable lesson:** <what to watch for next time — or "none">
```

Appendix A entries should be *genuinely useful* — the kind of thing that
saves the next person a day. If a mistake was trivial (a typo, a one-line
fix with no insight), **leave it out entirely** rather than padding the
appendix. An empty Appendix A is a valid document — write "None." in that
case; do not manufacture entries.

**Mandatory pre-finalization scan.** Before delivering, run the audit gate:

```bash
python3 <skill-dir>/scripts/audit_writeup.py <writeup.md>
```

It scans the main body for narration-of-correction phrases ("initially",
"at first", "turned out", "we had thought", "the bug", "failed",
"didn't work", "originally", "previously", "old approach", …). **Every hit
in the main body is either deleted or relocated to Appendix A.** The main
body should read as if everything worked the first time. Fix violations and
re-run until clean.

## Figures and diagrams

Generate figures with **XY** (`reflex-dev/xy`) — a Rust-backed,
GPU-accelerated Python charting library that exports to PNG, SVG, HTML, and
PDF.

**Setup and API.** Install with `pip install xy` (or `uv add xy`). A chart
is a container plus the marks inside it:

```python
import xy

chart = xy.line_chart(
    xy.line(x, y, color="#7c3aed", width=3),
    xy.theme(background="#ffffff", grid_color="#e6e6e1", text_color="#0b0b0b"),
    title="Throughput vs. worker count",
)
chart.to_png("figures/fig-01-throughput.png")
```

`xy.scatter_chart(xy.scatter(...))` covers scatter and density plots;
`density=True` plus a `colormap` handles large point clouds. `xy.theme(...)`
controls background, grid, axis, and text color. There is also a matplotlib
compatibility layer — `import xy.pyplot as plt` — if a pyplot-style
workflow is easier for a given figure.

**XY is alpha.** It is moving fast, and not every chart type is implemented
yet. Before writing plotting code, check the current docs at
`https://reflex.dev/docs/xy/` and the repo's capability matrix. If XY does
not yet support a chart type a figure needs (box plots, radar, treemap,
candlestick, and 3D are on the roadmap but may not have landed), **say so
in one line in the document** and fall back to plain matplotlib for that one
figure — never fake a chart type, never silently drop the figure.

**Rules for every figure:**

- Write and actually **run** the Python. Do not describe a figure you did
  not produce. The audit gate verifies each referenced figure file exists
  on disk; a dangling reference is a hard failure.
- Save to `figures/` alongside the Markdown, named `fig-01-<slug>.png`,
  numbered in document order.
- Reference with relative paths and a real caption:
  `![Fig 1: <what the reader should take away>](figures/fig-01-<slug>.png)`.
- Define **one** `xy.theme(...)` up front (in the first plotting script) and
  reuse it across every figure so the document is visually consistent. Do
  not load an unrelated styling skill unless the user asks for one by name.
- **Every figure must make a point.** Caption it with the *takeaway*, not
  the contents: "Throughput plateaus above 8 workers" — not "Throughput vs.
  worker count".
- Good candidates: results plots, before/after comparisons, parameter
  sweeps, distributions, large-N scatter. For architecture, data flow, and
  state machines, use a **Mermaid code block in the Markdown** instead — XY
  is a charting library, not a diagramming one.
- Put the full plotting script(s) in **Appendix C** so the figures are
  reproducible. **Pin the XY version** you used (`xy.__version__` or
  `pip show xy`).

## Glossary (Appendix B)

Every term defined in-line throughout the document also gets an entry here,
**alphabetized**, each with a one-sentence intuitive gloss and a
one-sentence precise definition:

```markdown
**<Term>.** <one-sentence intuitive gloss>. — *Precisely:* <one-sentence
formal definition>.
```

This is the reader's escape hatch when they jump into the middle of the
document. If a term is defined in-line, it must appear here. If Appendix B
is empty (no jargon was needed), write "None."

## Self-audit before delivering

Run the gate, then verify the checklist. Fix violations before handing the
file over — an audit failure is a defect in the deliverable, not a note:

```bash
python3 <skill-dir>/scripts/audit_writeup.py <writeup.md>
```

- [ ] Every section has a non-generic "Why this matters."
- [ ] Every section has both an intuitive and a technical pass, and they
      describe the same thing.
- [ ] No term appears before its definition.
- [ ] No corrections, debugging narration, or dead ends appear outside
      Appendix A. (Gate-enforced.)
- [ ] Every figure was actually generated and the file exists on disk.
      (Gate-enforced.)
- [ ] Every figure caption states a takeaway, not a content description.
- [ ] Every defined term appears in the glossary.
- [ ] A domain expert would find the technical passes rigorous enough to
      act on.
- [ ] A smart outsider could read only the intuitive passes and explain the
      project correctly.

The gate checks what is mechanically checkable (structure, figure
existence, correction-narration hits, glossary presence, section template
order). The judgment items (non-generic "why", same-thing passes, rigor)
are yours to verify by reading — the gate passing is necessary, not
sufficient.

## Deliverable

A single `.md` file plus a `figures/` directory, in the working directory
(or where the user specifies). Name the file after the project, slugified,
with the date:

```
<project-slug>-writeup-YYYY-MM-DD.md
```

(Use today's date; slug is lowercase hyphen-separated, e.g.
`engram-q3-validation-writeup-2026-09-20.md`.)

Hand both to the user: the file path and a one-paragraph orientation note
(tl;dr of the tl;dr, plus where the interesting detours live). Do not paste
the whole document into chat.

## Files

- `SKILL.md` — this file: the contract.
- `workflows/document-template.md` — fill-in-the-blanks skeleton for the
  output document.
- `workflows/self-audit.md` — the audit checklist plus how to run the gate.
- `workflows/figures.md` — XY figure conventions and the matplotlib
  fallback procedure.
- `scripts/audit_writeup.py` — the executable audit gate (stdlib only;
  runs on any Python ≥ 3.8).
- `examples/` — a complete reference write-up with a real figure, passing
  the gate. Read it before writing your first one.
