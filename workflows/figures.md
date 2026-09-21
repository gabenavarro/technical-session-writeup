# Figures

How to make figures for a write-up with XY (`reflex-dev/xy`), when to fall
back to matplotlib, and when to use Mermaid instead.

## Choose the right tool

| Figure kind | Tool |
|---|---|
| Results plots, before/after, parameter sweeps, distributions, large-N scatter | **XY** |
| Architecture, data flow, state machines, sequence-of-steps | **Mermaid** (a code block in the Markdown, not a file) |
| XY does not support the chart type | **matplotlib** for that one figure, with a one-line note in the document |

XY is a charting library, not a diagramming one. Do not force a flowchart
into XY, and do not force a density plot into Mermaid.

## XY procedure

1. **Check current capability first.** XY is alpha and moving fast. Before
   writing plotting code, confirm the chart type exists: docs at
   `https://reflex.dev/docs/xy/`, and the repo's capability matrix. If the
   type is not implemented (box, radar, treemap, candlestick, and 3D are on
   the roadmap, status may have changed), say so in one line in the
   document and use matplotlib for that figure.
2. **Pin the version.** Record `xy.__version__` (or `pip show xy`) and put
   it at the top of Appendix C.
3. **Define one theme up front.** The first plotting script sets a single
   `xy.theme(...)`; every later figure reuses it so the document is
   visually consistent.

```python
import xy

THEME = xy.theme(background="#ffffff", grid_color="#e6e6e1", text_color="#0b0b0b")
```

4. **Build the chart: container + marks.**

```python
chart = xy.line_chart(
    xy.line(x, y, color="#7c3aed", width=3),
    THEME,
    title="...",
)
```

Common forms:

```python
xy.line_chart(xy.line(x, y, ...), THEME, title="...")
xy.scatter_chart(xy.scatter(x, y, color="#0ea5e9", size=2), THEME, title="...")
xy.bar_chart(xy.bar(categories, values, color="#4f46e5"), THEME, title="...")
xy.area_chart(xy.area(x, y, opacity=0.4), THEME, title="...")
# large point clouds:
xy.scatter_chart(xy.scatter(x, y, density=True, colormap="viridis"), THEME, title="...")
```

A pyplot-style workflow is also available: `import xy.pyplot as plt`.

5. **Save to `figures/`** next to the Markdown, named `fig-NN-<slug>.png`,
   `NN` = document order.

```python
chart.to_png("figures/fig-01-<slug>.png")
```

6. **Run it for real.** Execute the script. Do not write a figure you did
   not produce. Confirm the file exists (`ls figures/`). The audit gate
   will reject a missing file.
7. **Reference it with a takeaway caption.**

```markdown
![Fig 1: Throughput plateaus above 8 workers](figures/fig-01-throughput.png)
```

The caption is the *point* of the figure, not its contents.
"Throughput plateaus above 8 workers" — not "Throughput vs. worker count".

## matplotlib fallback (one figure only)

When XY lacks the chart type:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7, 4))
ax.boxplot(data)
fig.savefig("figures/fig-02-box.png", dpi=150, bbox_inches="tight")
```

- Match the theme: set `fig.set_facecolor`, axis/spine colors, and font
  colors to the same values as `THEME`.
- Note in the document, in one line, why matplotlib was used for this
  figure ("XY 0.0.7 does not implement box plots; matplotlib used for
  Fig 2").
- Put the script in Appendix C alongside the XY scripts.

## Mermaid for structure

For architecture / data flow / state, write a Mermaid block directly in the
Markdown (the renderer — if the write-up is later rendered to HTML —
handles it; in raw Markdown it is still legible):

```markdown
```mermaid
flowchart LR
  A[Ingest] --> B[Transform] --> C[Store]
```
```

Give it a takeaway caption in the prose immediately before or after.
Do not emit a Mermaid PNG — the block is the figure.

## Anti-patterns

- **Decorative figures.** A figure that restates the prose adds nothing.
  If it does not let the reader see something the words cannot, cut it.
- **Faking a chart type.** Drawing a fake radar chart with lines is worse
  than a one-line matplotlib note.
- **Inconsistent styling.** Three different palettes across four figures
  makes the document look unowned. One theme, reused.
- **Contents captions.** "Figure of the results" is not a caption. State
  the takeaway.
