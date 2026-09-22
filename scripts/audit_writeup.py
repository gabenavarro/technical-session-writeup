#!/usr/bin/env python3
"""Audit gate for technical-session-writeup documents.

Stdlib only. Python >= 3.8.

Findings are split into two tiers:
  hard      - defects that block delivery (exit 1)
  advisory  - judgment-adjacent nudges (printed, exit 0)

Hard checks (mechanically verifiable subset of the skill's self-audit):
  1. Structure   - required H2 sections present, in order; exactly one H1.
  2. Template    - every technical section has Why-this-matters,
                   Intuitively, Technically passes, in order.
  3. Figures     - every technical section has at least one figure
                   (image reference or Mermaid block); every referenced
                   image file exists on disk.
  4. Corrections - no narration-of-correction phrases in the main body
                   (everything before Appendix A); code fences excluded.
  5. Appendices  - A has entries or "None."; B has entries or "None.";
                   C has a code fence when figures exist.

Advisories (warn, do not block):
  - a technical section has exactly one figure (density favors a second,
    e.g. structure + result)
  - a "Why this matters" opener shorter than 25 characters
  - an image with empty alt text

Usage:
  python3 audit_writeup.py [--json] <writeup.md | dir>
  python3 audit_writeup.py --version

A path may be a single Markdown file or a directory; a directory audits
every *.md in it (non-recursive, README files skipped).

With --json, prints per file:
  {"file": ..., "clean": bool,
   "hard": [[line, msg], ...], "advisories": [[line, msg], ...]}
For a directory, prints {"files": [ ... ], "clean": bool}.
"""

import argparse
import json
import re
import sys
from pathlib import Path

__version__ = "1.2.0"

# --- required H2 sections, in document order -------------------------------
REQUIRED_SECTIONS = [
    "TL;DR",
    "Why This Matters",
    "Background: What You Need to Know First",
    "Results",
    "What's Next",
    "Appendix A: Corrections and Dead Ends",
    "Appendix B: Glossary",
    "Appendix C: Reproducing the Figures",
]

# Technical section heading: "## Section N: ..." (N optional in the check).
SECTION_RE = re.compile(r"^##\s+(Section\s+\d+|Section|<Section)", re.IGNORECASE)

# Phrases that narrate corrections/debugging. Each is a finding when it
# appears in the main body (before Appendix A), outside code fences.
CORRECTION_PHRASES = [
    r"\binitially\b",
    r"\bin the beginning\b",
    r"\bat first\b",
    r"\boriginally\b",
    r"\bturned out\b",
    r"\bturns out\b",
    r"\bas it turned out\b",
    r"\bwe had thought\b",
    r"\bwe initially\b",
    r"\bthe bug\b",
    r"\ba bug\b",
    r"\bbugs\b",
    r"\bbroke\b",
    r"\bbroken\b",
    r"\bfailed\b",
    r"\bfailures?\b(?!\s+(mode|case|scenario|test|suite))",
    r"\bdidn't work\b",
    r"\bdid not work\b",
    r"\bdoesn't work\b",
    r"\bworkaround\b",
    r"\bstopgap\b",
    r"\bfirst attempt\b",
    r"\bfirst version\b",
    r"\binitial version\b",
    r"\binitial approach\b",
    r"\bolder approach\b",
    r"\bold approach\b",
    r"\bolder version\b",
    r"\bold version\b",
    r"\bafter debugging\b",
    r"\bafter some debugging\b",
    r"\bdebugging revealed\b",
    r"\bdead ?end",
    r"\bwe had to (fix|change|replace|switch|rewrite)\b",
    r"\bthe problem (was|turned out)\b",
    r"\bit (was|is) not (as|what)\b",
]

CODE_FENCE = re.compile(r"^(```|~~~)")
H1 = re.compile(r"^#\s+")
H2 = re.compile(r"^##\s+(.*)$")
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^\)]*)?\)")
IMG_ALT = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)")
GLOSSARY_ENTRY = re.compile(r"^\s*(?:[-*]\s+)?\*\*[^*]+\.\*\*", re.MULTILINE)
APPENDIX_A_ENTRY = re.compile(r"^###\s+A\.\d+", re.MULTILINE)
def strip_code_fences(lines):
    """Return lines with code-fence contents blanked out.

    The opening fence is replaced by a `[fence:<lang>]` placeholder so the
    fence *language* (e.g. `mermaid`) survives masking for checks that look
    for it; the fence body and closing fence are blanked. Fence delimiters are
    neutral for heading detection and phrase scanning.
    """
    masked = []
    in_fence = False
    for ln in lines:
        s = ln.strip()
        if CODE_FENCE.match(s):
            if in_fence:
                masked.append("")
            else:
                lang = s.lstrip("`~").strip()
                masked.append(f"[fence:{lang}]" if lang else "[fence]")
            in_fence = not in_fence
            continue
        masked.append("" if in_fence else ln)
    return masked


def heading_norm(title):
    return " ".join(title.split())


def find_h2(lines, title):
    for i, ln in enumerate(lines):
        m = H2.match(ln)
        if m and heading_norm(m.group(1)) == title:
            return i
    return None


def section_bounds(lines, start):
    """End index (exclusive) of the H2 section starting at `start`."""
    for i in range(start + 1, len(lines)):
        if H2.match(lines[i]) or H1.match(lines[i]):
            return i
    return len(lines)


def check(md_path: Path):
    """Return (hard_findings, advisory_findings); each is a list of
    (line_number, message) tuples."""
    hard = []
    adv = []
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    masked = strip_code_fences(lines)

    # 1. Exactly one H1 (fence-masked so comment lines in code do not count).
    h1s = [i for i, ln in enumerate(masked) if H1.match(ln)]
    if len(h1s) != 1:
        hard.append(
            (h1s[0] if h1s else 0, f"expected exactly one H1 title, found {len(h1s)}")
        )

    # 2. Required sections present, in order (detected on masked lines).
    idx = 0
    for title in REQUIRED_SECTIONS:
        pos = find_h2(masked, title)
        if pos is None:
            hard.append((idx + 1, f"missing required section: ## {title}"))
        elif pos < idx:
            hard.append((pos + 1, f"section out of order: ## {title}"))
        else:
            idx = pos

    # 3. At least one technical section with the template.
    tech = []
    for i, ln in enumerate(masked):
        m = H2.match(ln)
        if m and SECTION_RE.match(ln):
            tech.append((i, section_bounds(masked, i)))
    if not tech:
        hard.append((1, "no technical sections found (## Section N: ...)"))
    for start, end in tech:
        title = lines[start].strip()
        body = "\n".join(masked[start:end])
        why = re.search(r"why this matters", body, re.IGNORECASE)
        intu = re.search(r"\*\*Intuitively\.\*\*|\*\*Intuitively:", body, re.IGNORECASE)
        techp = re.search(r"\*\*Technically\.\*\*|\*\*Technically:", body, re.IGNORECASE)
        if not why:
            hard.append((start + 1, f"section '{title}' missing 'Why this matters'"))
        if not intu:
            hard.append((start + 1, f"section '{title}' missing **Intuitively.** pass"))
        if not techp:
            hard.append((start + 1, f"section '{title}' missing **Technically.** pass"))
        if why and intu and techp and not (why.start() < intu.start() < techp.start()):
            hard.append((start + 1, f"section '{title}' parts out of order (Why -> Intuitively -> Technically)"))
        # Hard: every technical section must carry at least one figure
        # (an image reference or a Mermaid block). The skill's policy is
        # that more figures is better than fewer, so a section with zero is
        # a defect, not a permitted omission.
        figs = sum(1 for _ in IMG.finditer(body))
        if figs == 0 and "mermaid" not in body.lower():
            hard.append(
                (start + 1, f"section '{title}' has no figure (add a diagram or plot)")
            )
        # Advisory: a section with exactly one figure could usually carry a
        # second (structure + result); nudge toward density.
        elif figs == 1 and "mermaid" not in body.lower():
            adv.append(
                (start + 1, f"section '{title}' has one figure - consider a second (e.g. structure + result)")
            )

    # 4. Figures exist on disk (references inside code fences are literals, skipped).
    for i, ln in enumerate(masked):
        for m in IMG.finditer(ln):
            src = m.group(1)
            if re.match(r"^(https?:|data:|//)", src):
                continue
            rel = Path(src.split("?")[0])
            if not (md_path.parent / rel).exists():
                hard.append((i + 1, f"figure file missing: {src}"))
        for m in IMG_ALT.finditer(ln):
            if m.group(1).strip() == "":
                adv.append((i + 1, f"image has empty alt text: ({m.group(2)[:40]})"))

    # 5. Corrections rule: main body only (before Appendix A).
    app_a = find_h2(masked, "Appendix A: Corrections and Dead Ends")
    body_end = app_a if app_a is not None else len(lines)
    for i, ln in enumerate(masked[:body_end]):
        if not ln:
            continue
        for pat in CORRECTION_PHRASES:
            if re.search(pat, ln, re.IGNORECASE):
                hard.append((i + 1, f"correction narration in main body: {ln.strip()[:70]}"))
                break  # one finding per line

    # 6. Appendix content rules.
    for title, entry_re in [
        ("Appendix A: Corrections and Dead Ends", APPENDIX_A_ENTRY),
        ("Appendix B: Glossary", GLOSSARY_ENTRY),
    ]:
        pos = find_h2(masked, title)
        if pos is None:
            continue  # already reported
        end = section_bounds(masked, pos)
        seg = "\n".join(lines[pos:end])
        if "None." not in seg and not entry_re.search(seg):
            hard.append((pos + 1, f"{title}: must contain entries or 'None.'"))

    pos_c = find_h2(masked, "Appendix C: Reproducing the Figures")
    if pos_c is not None:
        end = section_bounds(masked, pos_c)
        seg = "\n".join(lines[pos_c:end])
        has_fig = any(IMG.search(ln) for ln in masked)
        if has_fig and "```" not in seg and "None." not in seg:
            hard.append((pos_c + 1, "Appendix C: figures exist but no reproducible plotting script found"))

    return hard, adv


def audit_one(md: Path):
    """Audit a single file; return sorted (hard, adv) or None if missing."""
    if not md.exists():
        return None
    hard, adv = check(md)
    hard.sort()
    adv.sort()
    return hard, adv


def collect_targets(target: Path):
    """Resolve a target to a list of Markdown files to audit.

    A file is returned as-is; a directory yields its *.md files,
    non-recursive, skipping README files (orientation, not write-ups).
    """
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(p for p in target.glob("*.md") if p.name != "README.md")
    return []


def print_human(md: Path, hard, adv):
    if hard:
        print(f"audit: {len(hard)} hard finding(s) in {md.name}:")
        for lineno, msg in hard:
            print(f"  L{lineno}: {msg}")
    if adv:
        print(f"audit: {len(adv)} advisory(ies) in {md.name} (review, non-blocking):")
        for lineno, msg in adv:
            print(f"  L{lineno}: {msg}")
    if not hard:
        print(f"audit: clean ({md.name})" if not adv else f"audit: clean with advisories ({md.name})")


def main():
    parser = argparse.ArgumentParser(
        description="Audit technical-session-writeup documents."
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="a write-up Markdown file, or a directory of *.md files "
        "(non-recursive, README files skipped)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON"
    )
    parser.add_argument(
        "--version", action="store_true", help="print gate version and exit"
    )
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return 0
    if args.target is None:
        parser.error("target is required unless --version is given")

    target = Path(args.target)
    files = collect_targets(target)
    if not files:
        if args.json:
            print(
                json.dumps(
                    {"file": str(target), "clean": False, "error": "not found"}
                )
            )
        else:
            print(f"audit: not found: {target}")
        return 2

    results = []
    for f in files:
        r = audit_one(f)
        if r is None:
            if args.json:
                print(
                    json.dumps(
                        {"file": str(f), "clean": False, "error": "not found"}
                    )
                )
            else:
                print(f"audit: not found: {f}")
            return 2
        results.append((f, r[0], r[1]))

    is_dir = target.is_dir()
    all_hard = sum(len(hard) for _, hard, _ in results)

    if args.json:
        if is_dir:
            payload = {
                "files": [
                    {
                        "file": str(f),
                        "clean": not hard,
                        "hard": [[n, m] for n, m in hard],
                        "advisories": [[n, m] for n, m in adv],
                    }
                    for f, hard, adv in results
                ],
                "clean": all_hard == 0,
            }
        else:
            f, hard, adv = results[0]
            payload = {
                "file": str(f),
                "clean": not hard,
                "hard": [[n, m] for n, m in hard],
                "advisories": [[n, m] for n, m in adv],
            }
        print(json.dumps(payload, indent=2))
        return 1 if all_hard else 0

    if is_dir:
        for f, hard, adv in results:
            print_human(f, hard, adv)
            print()
        print(f"audit: {all_hard} hard finding(s) across {len(results)} file(s)")
    else:
        f, hard, adv = results[0]
        print_human(f, hard, adv)
    return 1 if all_hard else 0


if __name__ == "__main__":
    sys.exit(main())
