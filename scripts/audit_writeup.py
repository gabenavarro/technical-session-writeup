#!/usr/bin/env python3
"""md2html-free audit gate for technical-session-writeup documents.

Stdlib only. Python >= 3.8. Exits 0 when the write-up is clean, 1 with
line-numbered findings otherwise.

Checks (mechanically verifiable subset of the skill's self-audit):
  1. Structure  - required H2 sections present, in order; exactly one H1.
  2. Template   - every technical section has Why-this-matters,
                  Intuitively, Technically passes, in order.
  3. Figures    - every referenced image file exists on disk.
  4. Corrections- no narration-of-correction phrases in the main body
                  (everything before Appendix A); code fences excluded.
  5. Appendices - A has entries or "None."; B has entries or "None.";
                  C has a code fence when figures exist.

Usage:
  python3 audit_writeup.py <writeup.md>
"""

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
GLOSSARY_ENTRY = re.compile(r"^\s*(?:[-*]\s+)?\*\*[^*]+\.\*\*", re.MULTILINE)
APPENDIX_A_ENTRY = re.compile(r"^###\s+A\.\d+", re.MULTILINE)


def strip_code_fences(lines):
    """Return (lines_with_fences_masked, fence_line_numbers)."""
    masked = []
    in_fence = False
    for ln in lines:
        if CODE_FENCE.match(ln.strip()):
            in_fence = not in_fence
            masked.append("")  # fence delimiter itself is neutral
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
    findings = []
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    masked = strip_code_fences(lines)

    # 1. Exactly one H1 (fence-masked so comment lines in code do not count).
    h1s = [i for i, ln in enumerate(masked) if H1.match(ln)]
    if len(h1s) != 1:
        findings.append(
            (h1s[0] if h1s else 0, f"expected exactly one H1 title, found {len(h1s)}")
        )

    # 2. Required sections present, in order (detected on masked lines).
    idx = 0
    for title in REQUIRED_SECTIONS:
        pos = find_h2(masked, title)
        if pos is None:
            findings.append((idx + 1, f"missing required section: ## {title}"))
        elif pos < idx:
            findings.append((pos + 1, f"section out of order: ## {title}"))
        else:
            idx = pos

    # 3. At least one technical section with the template.
    tech = []
    for i, ln in enumerate(masked):
        m = H2.match(ln)
        if m and SECTION_RE.match(ln):
            tech.append((i, section_bounds(masked, i)))
    if not tech:
        findings.append((1, "no technical sections found (## Section N: ...)"))
    for start, end in tech:
        title = lines[start].strip()
        body = "\n".join(masked[start:end])
        why = re.search(r"why this matters", body, re.IGNORECASE)
        intu = re.search(r"\*\*Intuitively\.\*\*|\*\*Intuitively:", body, re.IGNORECASE)
        techp = re.search(r"\*\*Technically\.\*\*|\*\*Technically:", body, re.IGNORECASE)
        if not why:
            findings.append((start + 1, f"section '{title}' missing 'Why this matters'"))
        if not intu:
            findings.append((start + 1, f"section '{title}' missing **Intuitively.** pass"))
        if not techp:
            findings.append((start + 1, f"section '{title}' missing **Technically.** pass"))
        if why and intu and techp and not (why.start() < intu.start() < techp.start()):
            findings.append((start + 1, f"section '{title}' parts out of order (Why -> Intuitively -> Technically)"))

    # 4. Figures exist on disk (references inside code fences are literals, skipped).
    for i, ln in enumerate(masked):
        for m in IMG.finditer(ln):
            src = m.group(1)
            if re.match(r"^(https?:|data:|//)", src):
                continue
            rel = Path(src.split("?")[0])
            if not (md_path.parent / rel).exists():
                findings.append((i + 1, f"figure file missing: {src}"))

    # 5. Corrections rule: main body only (before Appendix A).
    app_a = find_h2(masked, "Appendix A: Corrections and Dead Ends")
    body_end = app_a if app_a is not None else len(lines)
    for i, ln in enumerate(masked[:body_end]):
        if not ln:
            continue
        for pat in CORRECTION_PHRASES:
            if re.search(pat, ln, re.IGNORECASE):
                findings.append((i + 1, f"correction narration in main body: {ln.strip()[:70]}"))
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
            findings.append((pos + 1, f"{title}: must contain entries or 'None.'"))

    pos_c = find_h2(masked, "Appendix C: Reproducing the Figures")
    if pos_c is not None:
        end = section_bounds(masked, pos_c)
        seg = "\n".join(lines[pos_c:end])
        has_fig = any(IMG.search(ln) for ln in masked)
        if has_fig and "```" not in seg and "None." not in seg:
            findings.append((pos_c + 1, "Appendix C: figures exist but no reproducible plotting script found"))

    return findings


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    md = Path(sys.argv[1])
    if not md.exists():
        print(f"audit: not found: {md}")
        return 2
    findings = check(md)
    if findings:
        print(f"audit: {len(findings)} finding(s) in {md.name}:")
        for lineno, msg in sorted(findings):
            print(f"  L{lineno}: {msg}")
        return 1
    print(f"audit: clean ({md.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
