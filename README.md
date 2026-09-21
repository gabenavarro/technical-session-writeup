# technical-session-writeup

A portable [Agent Skill](https://github.com/anthropics/skills) that turns a
technical working session into **one Markdown write-up** readable by both a
brilliant non-specialist and a domain expert.

It exists to fix four failure modes of technical documentation:

1. **Undefined jargon** — terms used without definition.
2. **Zombie problems** — fixed bugs and dead ends narrated in the main body
   as if they were still open.
3. **Missing "why"** — mechanical detail without purpose.
4. **One-audience writing** — an altitude that serves the expert or the
   outsider, never both.

## Output shape

```
# <Title>
## TL;DR
## Why This Matters
## Background: What You Need to Know First
## Section 1..N      (each: Why this matters / Intuitively / Technically / Figure)
## Results
## What's Next
## Appendix A: Corrections and Dead Ends
## Appendix B: Glossary
## Appendix C: Reproducing the Figures
```

Figures are generated with [XY](https://github.com/reflex-dev/xy) (Rust-backed,
GPU-accelerated Python charting, exports PNG/SVG/HTML/PDF); architecture
diagrams use Mermaid; unsupported chart types fall back to matplotlib with a
one-line note.

## Install (any machine, any harness)

```bash
git clone https://github.com/gabenavarro/technical-session-writeup
```

The only runtime requirement for the audit gate is Python ≥ 3.8 (stdlib
only). XY is needed only to produce figures: `pip install xy` (or
`uv add xy`).

**OMP** — `skills.customDirectories: ["/path/to/technical-session-writeup"]`,
or copy/symlink into `~/.agent/skills/` (user) / `.github/skills/` (project).

**Claude Code / any Agent Skills harness** — drop the folder into the skills
directory; `SKILL.md` at the root is the contract.

## Usage

Invoke it at the end of a technical session: "write this up", "summarize the
session", "document what we did". It produces:

```
<project-slug>-writeup-YYYY-MM-DD.md   +   figures/
```

## The audit gate

```bash
python3 scripts/audit_writeup.py <writeup.md>
```

Mechanically verifies: required structure and order, per-section template
(Why / Intuitively / Technically), figure files exist on disk, no
correction-narration phrases in the main body, appendices populated. Exit 0
= clean. The gate is necessary, not sufficient — the judgment checklist in
`workflows/self-audit.md` (same-thing check, outsider test, rigor) still
applies.

## Layout

```
SKILL.md                        the skill contract
workflows/document-template.md  fill-in skeleton for the output
workflows/self-audit.md         audit checklist + gate usage
workflows/figures.md            XY conventions + matplotlib fallback
scripts/audit_writeup.py        executable audit gate (stdlib only)
examples/                       reference write-up + real figure (passes the gate)
```

## License

MIT
