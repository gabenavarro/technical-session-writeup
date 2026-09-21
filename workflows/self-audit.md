# Self-Audit

Run this before delivering. The gate enforces what is mechanically
checkable; the checklist covers what only a reader can judge. Both must
pass.

## 1. Run the gate (mechanical checks)

```bash
python3 <skill-dir>/scripts/audit_writeup.py <writeup.md>
```

Exit 0 with no findings is required. The gate checks:

- **Structure:** all required `##` headings present, in order.
- **Section template:** every numbered technical section has a "Why this
  matters" lead, an `**Intuitively.**` pass, and a `**Technically.**` pass,
  in that order.
- **Figures exist:** every `![...](...)` image reference resolves to a file
  on disk (relative to the Markdown file). Dangling figure references are
  hard failures — a figure you did not produce is a defect.
- **Corrections rule:** scans the main body (everything before Appendix A)
  for narration-of-correction phrases. Each hit is a finding you must fix
  by deleting the phrase or relocating the content to Appendix A.
- **Glossary:** Appendix B exists and is non-empty (or explicitly "None.").
- **Appendices:** A, B, and C are all present.

The gate is stdlib-only Python (≥ 3.8) — it runs on any machine with a
Python interpreter, no install step.

## 2. The judgment checklist (human checks)

The gate passing is **necessary, not sufficient**. Verify each of these by
reading:

- [ ] Every section's "Why this matters" is **non-generic**. Read it in
      isolation: does it name what specifically breaks without *this*
      component, or is it a sentence that could open any section ("this
      improves performance")? If the latter, rewrite it.
- [ ] **Same-thing check.** For each section, cover the Technical pass and
      read the Intuitive pass, then predict what the Technical pass says.
      If your prediction is off — the analogy drifted to a different
      concept — the section is broken. Fix the analogy so it formalizes
      into the technical version.
- [ ] **No term before definition.** Read top to bottom. At every first
      use of a jargon term, is there an in-line definition in the same
      sentence or the one before? If not, define it (and add it to the
      glossary).
- [ ] **No zombie problems.** Scan the main body for any implication that
      a fixed bug is still open, a dead end is live, or work is in
      progress when it is done. The main body reports the final state only.
- [ ] **Rigor for the expert.** Would a domain expert have enough
      equations, bounds, versions, and citations to act on the Technical
      passes? Vague Technical passes are as bad as vague Intuitive ones.
- [ ] **Outsider test.** Read *only* the Intuitive passes (plus TL;DR and
      Background). Can you now explain the project correctly to someone?
      If not, the ladders have gaps — strengthen Background or the
      analogies.
- [ ] **Captions make a point.** Every figure caption states the takeaway,
      not the contents.
- [ ] **Glossary completeness.** Every in-line defined term has a
      glossary entry.

## 3. Fix-and-re-run loop

1. Run the gate.
2. Fix every finding (relocate narration to Appendix A, add missing
   structure, create missing figure files, add glossary entries).
3. Re-run the gate until clean.
4. Work the judgment checklist.
5. Deliver.

A clean gate plus a checked checklist is the definition of done for this
skill.
