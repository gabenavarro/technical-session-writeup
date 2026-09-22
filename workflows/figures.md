# Figures

How to make figures for a write-up. Figures live **in the Markdown as
fenced blocks** (preferred) or as image files (fallback). The audit gate
counts `fig`, `xy`, `svg`, and `mermaid` fences as figures, and image
references.

## Density: err on the side of many

The policy is that **more figures is better than fewer.** A document that
is easy to follow beats one that is lean. Concretely:

- Every technical section must have **at least one** figure (the audit gate
  enforces this). One is the floor, not the target.
- The common shape is **two per section**: a Mermaid structure/flow
  diagram (how the pieces fit) *and* a `fig` plot (what it produces,
  measured). Include both when the section supports it.
- When a section has exactly one figure, the audit gate will flag it as an
  advisory — treat the nudge as a prompt to add a second angle.
- The only real limit is quality: each figure must make at least a small
  point (a takeaway caption). Do not invent a chart for its own sake, but
  do not ration figures — a spare diagram is a trivial defect, a wall of
  prose is not.

## Choose the right tool

| Figure kind | Form |
|---|---|
| Results plots, before/after, parameter sweeps, distributions | **`fig` fence** (matplotlib, static, theme-aware) |
| Large-N scatter, anything the reader should pan/zoom/inspect | **`xy` fence** (interactive) |
| Architecture, data flow, state machines, sequence-of-steps | **`mermaid` fence** |
| Pre-rendered / binary / external-tool image | **image file** fallback |

Charts are matplotlib-based by default: a `fig` fence runs under a themed
context and is inlined into the rendered report as dual-theme SVG. `xy`
is for interactivity. Mermaid is for structure — it is a diagramming
format, not a charting one. Do not force a flowchart into a plot, and do
not force a density plot into Mermaid.

## `fig` procedure (primary)

1. **Write a self-contained matplotlib script.** Import what you use;
   inline or derive the data. The script runs in an isolated namespace.
2. **Use the themed namespace.** The fence is executed with:
   - `plt` — matplotlib.pyplot, pre-styled for the active theme;
   - `C` — palette dict (`coral, teal, orange, purple, red, blue, green,
     ink, muted, line, bg`). Use semantic colors so light **and** dark
     both read;
   - `clean(ax)` — removes top/right spines, thins the grid;
   - `save()` — saves the current figure (or `fig` global) to the output
     SVG.
3. **Label it.** Set a title and axis labels. `figsize` ≈ `(6.5, 3.6)`.
4. **Run it for real.** The source must execute in a scratch dir — do not
   write a figure you did not produce.
5. **Caption with the takeaway** on the line after the closing fence:

````markdown
```fig
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.plot(workers, tput, color=C["coral"], lw=2.5)
ax.set_title("Throughput vs. worker count")
ax.set_xlabel("workers"); ax.set_ylabel("seq / s")
clean(ax)
save()
```
Fig 1: Throughput plateaus above 8 workers.
````

The caption is the *point* of the figure, not its contents.
"Throughput plateaus above 8 workers" — not "Throughput vs. worker count".

## `xy` procedure (interactive)

Use when the reader should pan/zoom/inspect (large-N data, live
exploration). XY (`reflex-dev/xy`) is a Rust-backed Python charting
library; a chart is a container plus the marks inside it:

1. **Check current capability first.** XY is alpha and moving fast. Before
   writing plotting code, confirm the chart type exists: docs at
   `https://reflex.dev/docs/xy/`, and the repo's capability matrix. If the
   type is not implemented, **say so in one line in the document** and use
   a `fig` fence for that figure — never fake a chart type, never silently
   drop the figure.
2. **Pin the version.** Record `xy.__version__` (or `pip show xy`) and put
   it at the top of Appendix C.
3. **Build the chart: container + marks**, bound to a module-level variable
   named `chart` inside the fence:

````markdown
```xy
import xy
chart = xy.line_chart(
    xy.line(x, y, color="#7c3aed", width=3),
    title="...",
)
```
````

Common forms:

```python
xy.line_chart(xy.line(x, y, ...), title="...")
xy.scatter_chart(xy.scatter(x, y, color="#0ea5e9", size=2), title="...")
xy.bar_chart(xy.bar(categories, values, color="#4f46e5"), title="...")
xy.area_chart(xy.area(x, y, opacity=0.4), title="...")
# large point clouds:
xy.scatter_chart(xy.scatter(x, y, density=True, colormap="viridis"), title="...")
```

`xy.theme(...)` sets background/grid/text color; defaults track the report
theme automatically, so a single consistent theme is the default — don't
override per figure. A pyplot-style layer (`import xy.pyplot as plt`) is
also available.
4. **Caption with the takeaway** on the line after the closing fence.

## Image file (fallback)

When a figure can't be a fence (pre-rendered, binary, external tool):

1. Save to `figures/` next to the Markdown, named `fig-NN-<slug>.png`,
   `NN` = document order.
2. **Run it for real.** Do not write a figure you did not produce. The
   audit gate rejects a missing file.
3. **Reference it with a takeaway caption:**

```markdown
![Fig 1: Throughput plateaus above 8 workers](figures/fig-01-throughput.png)
```

## Mermaid for structure

For architecture / data flow / state, write a Mermaid block directly in the
Markdown (the renderer — if the write-up is later rendered to HTML —
handles it; in raw Markdown it is still legible):

````markdown
```mermaid
flowchart LR
  A[Ingest] --> B[Transform] --> C[Store]
```
````

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
