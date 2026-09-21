#!/usr/bin/env python3
"""Reproduce the example's figures.

Run:  python3 scripts/make_figures.py   (xy must be installed)
Requires: xy (pinned in the write-up's Appendix C)

Fig 1: audit-gate findings across the three draft revisions of this
       document (draft 0: no structure, draft 1: structure added,
       final: clean).
Fig 2: read-time network requests per asset class, CDN approach (one
       fetch) vs. md2html's inlined output (zero).
"""

from pathlib import Path

import xy
THEME = xy.theme(background="#ffffff", grid_color="#e6e6e1", text_color="#0b0b0b")
HERE = Path(__file__).parent.parent / "figures"
HERE.mkdir(parents=True, exist_ok=True)

# Fig 1
drafts = ["draft 0", "draft 1", "final"]
findings = [5, 3, 0]
chart = xy.bar_chart(
    xy.bar(drafts, findings, color="#dc2626", name="audit findings"),
    THEME,
    title="Audit gate findings by revision",
)
chart.to_png(str(HERE / "fig-01-audit-gate.png"))

# Fig 2
# Fig 2 — before/after: read-time network requests per asset class,
# CDN loading (old) vs. inlined (new).
assets = ["CSS", "Mermaid bundle", "KaTeX fonts", "Shiki (runtime)"]
cdn = [1, 1, 1, 1]     # one fetch at read time under the old approach
inlined = [0, 0, 0, 0] # zero fetches: all inlined at build time
chart2 = xy.bar_chart(
    xy.bar(assets, cdn, color="#dc2626", name="CDN (read-time fetch)"),
    xy.bar(assets, inlined, color="#16a34a", name="md2html (inlined)"),
    THEME,
    title="Read-time network requests per asset class: CDN vs. inlined",
)
chart2.to_png(str(HERE / "fig-02-offline-assets.png"))
