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
  3. Figures     - every referenced image file exists on disk.
  4. Corrections - no narration-of-correction phrases in the main body
                   (everything before Appendix A); code fences excluded.
  5. Appendices  - A has entries or "None."; B has entries or "None.";
                   C has a code fence when figures exist.

Advisories (warn, do not block):
  - a technical section has no Figure (the skill permits omission, but it
    is worth a second look)
  - a "Why this matters" opener shorter than 25 characters
  - an image with empty alt text

Usage:
  python3 audit_writeup.py [--json] <writeup.md>

With --json, prints:
  {"file": ..., "clean": bool,
   "hard": [[line, msg], ...], "advisories": [[line, msg], ...]}
"""

import argparse
import json
import re
import sys
from pathlib import Path

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

    Fence delimiters themselves are blanked too; they are neutral for
    heading detection and phrase scanning.
    """
    masked = []
    in_fence = False
    for ln in lines:
        if CODE_FENCE.match(ln.strip()):
            in_fence = not in_fence
            masked.append("")
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
        # Advisories: short opener, missing figure.
        if why and intu and why.start() < intu.start():
            opener = body[why.end():intu.start()].strip()
            if len(opener) < 25:
                adv.append((start + 1, f"section '{title}' 'Why this matters' opener is short (< 25 chars)"))
        if "!" not in body and "mermaid" not in body.lower():
            adv.append((start + 1, f"section '{title}' has no Figure (permitted - verify it adds nothing)"))

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


def main():
    parser = argparse.ArgumentParser(
        description="Audit a technical-session-writeup document."
    )
    parser.add_argument("writeup", help="path to the write-up Markdown file")
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON"
    )
    args = parser.parse_args()

    md = Path(args.writeup)
    if not md.exists():
        if args.json:
            print(json.dumps({"file": str(md), "clean": False, "error": "not found"}))
        else:
            print(f"audit: not found: {md}")
        return 2

    hard, adv = check(md)
    hard.sort()
    adv.sort()

    if args.json:
        print(
            json.dumps(
                {
                    "file": str(md),
                    "clean": not hard,
                    "hard": [[n, m] for n, m in hard],
                    "advisories": [[n, m] for n, m in adv],
                },
                indent=2,
            )
        )
        return 1 if hard else 0

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
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
