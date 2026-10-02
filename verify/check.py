#!/usr/bin/env python3
"""
Independent provenance checker for the Lead Magnet Translator.

Optional. Not part of normal use. A real translation runs entirely inside a
Claude Project chat and never calls this script. This exists so a skeptical
reader can verify, by running actual code rather than trusting the AI's own
self-check, that every quoted fragment in a companion sources file genuinely
appears in the transcript (or notes) it claims to come from.

The reader-facing ideas menu itself carries one headline transcript quote
per idea (see rules.md section 4, part 7), but the full grounding, every
claim and quote behind each idea, lives in a separate companion file, named
sources-[YYYY-MM-DD].txt, delivered alongside the menu. That companion file
is what this script checks.

Usage:
    python check.py <sources-file.txt> <transcript-file.txt> [notes-file.txt]
    python check.py <sources-file.txt> <transcript-file.txt> [notes-file.txt] --menu <menu-file.txt>
    python check.py --selftest

The notes file is optional, and only needed if the sources file contains any
NOTES lines (see below). Without it, NOTES lines are skipped with a warning
rather than checked.

--selftest runs this script against its own two shipped fixtures instead of
checking real output: the known-good sources file (test-cases/correct-
sources.txt, which must pass in full) and the known-broken one (test-cases/
broken-sources.txt, which must fail on every single line). It exists so a
reader doesn't have to take this script's correctness on faith either --
the same discipline this whole tool asks of the AI's output applies to the
checker meant to verify it. See the "What --selftest actually proves"
section below for what a pass here does and doesn't establish.

A sources file contains one or more blocks in this form:

    IDEA: The "Say It Out Loud" Pricing Script
    CLAIM: One attendee asked for the exact words as a script.
    SOURCE: "Can we just get the actual words? Like a script?" — around line 24

A block can have more than one SOURCE line if more than one part of the
transcript supports the same claim. An idea can also have more than one
block, one per distinct claim. If call notes were supplied, a block can also
carry a NOTES line, alongside any SOURCE line, when a note backs the same
claim as the transcript quote:

    IDEA: The "Say It Out Loud" Pricing Script
    CLAIM: The business owner had already noticed this gap themselves.
    SOURCE: "Can we just get the actual words? Like a script?" — around line 24
    NOTES: "kept meaning to write a script for the pricing moment"

IDEA and CLAIM are read but not verified against anything -- they document
which idea a claim belongs to and what it says. SOURCE lines are checked
against the transcript; NOTES lines are checked against the notes file, if
one was given. Every idea must have at least one SOURCE line somewhere
across its block or blocks; a NOTES line can add weight to a claim, but
never stands alone as an idea's only grounding, and this script flags any
idea that has NOTES lines but no SOURCE line anywhere as a failure.

For each SOURCE or NOTES line, the script checks:
  1. The quoted fragment appears somewhere in its source text, exactly
     (ignoring case and extra whitespace) -- not paraphrased, not close.
  2. For a SOURCE line, if a line number is given in the reference (e.g.
     "around line 24" or "line 24"), the fragment is checked first in a
     window around that line; if it isn't found there, the whole transcript
     is searched as a fallback, and the result says so, since this tool's
     line references are approximate ("around line N"), not an exact
     pointer. NOTES lines carry no line reference and are checked against
     the whole notes file.

On any failure it prints the claim, what was searched for, and where (if
anywhere) it was actually found, then exits non-zero. It never modifies any
input file.

--menu also checks the menu itself, which the sources check never reads
(it only reads the sources file). Mechanical rules:
  0. The menu has exactly five slots (IDEA 1 to IDEA 5), each either a full
     idea (has a Title) or a marked gap ("No idea:"), and every quote in the
     NOT USED list appears in the transcript.
Two more, on menu text outside the Source and NOT USED lines:
  1. Reaction and timing words ("visibly", "surprised", "whole room",
     "everyone", "within a minute", "nodding", ...) fail unless that exact
     phrase appears inside a verified SOURCE or NOTES quote.
  2. A count of people ("two attendees", "both attendees", "three people")
     fails unless the sources file has a CLAIM with the same wording AND that
     claim's SOURCE quotes come from at least that many different speakers.
Limit, stated plainly: this catches invented reactions, timing and counts. It
cannot tell whether a quote from a second speaker actually does what the claim
says (two people both quoted does not prove two people both "asked"), so a
passing count claim is printed for a human to read, not trusted.

What --selftest actually proves: that this script correctly passes a menu
built the way rules.md describes, and correctly fails one where every single
quote is either invented outright or subtly altered from the real transcript
line. It is not a guarantee this script catches every possible way a quote
could be wrong, only that it catches the two shapes of wrong its own shipped
fixture demonstrates. Treat a --selftest pass as "the checker's basic logic
works," not "every future sources file this checker approves is trustworthy
by that fact alone."
"""

import re
import sys
from pathlib import Path

LINE_WINDOW = 3  # lines above/below a referenced line also checked, since
                  # "around line N" is an approximate pointer, not exact.

BLOCK = re.compile(
    r'IDEA:\s*(?P<idea>.+?)\s*\n'
    r'CLAIM:\s*(?P<claim>.+?)\s*\n'
    r'(?P<lines>(?:(?:SOURCE|NOTES):.*\n?)+)',
)

SOURCE_LINE = re.compile(
    r'SOURCE:\s*"(?P<quote>[^"]+)"\s*—\s*(?P<ref>.+)',
)

NOTES_LINE = re.compile(
    r'NOTES:\s*"(?P<quote>[^"]+)"',
)

LINE_NUMBER = re.compile(r'line\s+(\d+)', re.IGNORECASE)


def normalise(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def check_source(quote, ref, transcript_lines, full_text_normalised):
    quote_norm = normalise(quote)

    m = LINE_NUMBER.search(ref)
    if m:
        line_no = int(m.group(1))
        window_start = max(0, line_no - 1 - LINE_WINDOW)
        window_end = min(len(transcript_lines), line_no + LINE_WINDOW)
        window_text = normalise(" ".join(transcript_lines[window_start:window_end]))
        if quote_norm in window_text:
            return True, f"found near line {line_no}, as referenced"

        # Fallback: search the whole transcript, since the reference is
        # approximate by design ("around line N"), not an exact pointer.
        if quote_norm in full_text_normalised:
            return True, (
                f"NOTE: not found near line {line_no} as referenced, but found "
                f"elsewhere in the transcript. Check the line reference is accurate"
            )
        return False, f"not found near line {line_no}, or anywhere else in the transcript"

    # No line number given at all: search the whole transcript.
    if quote_norm in full_text_normalised:
        return True, "found in transcript (no line reference given to narrow the search)"
    return False, "not found anywhere in the transcript"


def check_notes(quote, notes_text_normalised):
    quote_norm = normalise(quote)
    if quote_norm in notes_text_normalised:
        return True, "found in the supplied notes file"
    return False, "not found anywhere in the supplied notes file"


def run_check(sources_path, transcript_path, notes_path=None):
    """Runs the full check and returns (exit_code, failures, total_checked,
    total_blocks). Prints its findings as it goes, same as always."""

    if not sources_path.exists():
        print(f"Sources file not found: {sources_path}")
        return 2, None, None, None
    if not transcript_path.exists():
        print(f"Transcript file not found: {transcript_path}")
        return 2, None, None, None
    if notes_path is not None and not notes_path.exists():
        print(f"Notes file not found: {notes_path}")
        return 2, None, None, None

    sources_text = sources_path.read_text(encoding="utf-8")
    transcript_lines = transcript_path.read_text(encoding="utf-8").splitlines()
    full_text_normalised = normalise(" ".join(transcript_lines))

    notes_text_normalised = None
    if notes_path is not None:
        notes_text_normalised = normalise(notes_path.read_text(encoding="utf-8"))

    blocks = list(BLOCK.finditer(sources_text))

    if not blocks:
        print(f"No IDEA/CLAIM/SOURCE blocks found in {sources_path}")
        return 2, None, None, None

    ideas_seen = set()
    ideas_with_failure = set()
    total_sources = 0
    total_notes = 0
    failures = 0
    for block_match in blocks:
        idea = block_match.group("idea").strip()
        claim = block_match.group("claim").strip()
        block_lines = block_match.group("lines")
        source_lines = list(SOURCE_LINE.finditer(block_lines))
        notes_lines = list(NOTES_LINE.finditer(block_lines))
        ideas_seen.add(idea)

        print(f"[{idea}] {claim}")
        if not source_lines:
            print("      FAIL  no SOURCE line in this block, a NOTES line alone is never enough")
            failures += 1
            ideas_with_failure.add(idea)
            print()
            continue

        for s in source_lines:
            total_sources += 1
            quote = s.group("quote")
            ref = s.group("ref").strip()
            ok, detail = check_source(quote, ref, transcript_lines, full_text_normalised)
            short_quote = quote[:60] + ("..." if len(quote) > 60 else "")
            if ok:
                print(f'  PASS  SOURCE "{short_quote}"')
                print(f"        {detail}")
            else:
                failures += 1
                ideas_with_failure.add(idea)
                print(f'  FAIL  SOURCE "{short_quote}"')
                print(f"        {detail}")

        for n in notes_lines:
            total_notes += 1
            quote = n.group("quote")
            short_quote = quote[:60] + ("..." if len(quote) > 60 else "")
            if notes_text_normalised is None:
                print(f'  SKIP  NOTES "{short_quote}"')
                print("        no notes file given, pass it as a third argument to check this")
                continue
            ok, detail = check_notes(quote, notes_text_normalised)
            if ok:
                print(f'  PASS  NOTES "{short_quote}"')
                print(f"        {detail}")
            else:
                failures += 1
                ideas_with_failure.add(idea)
                print(f'  FAIL  NOTES "{short_quote}"')
                print(f"        {detail}")
        print()

    total_checked = total_sources + total_notes
    ideas_clean = len(ideas_seen) - len(ideas_with_failure)
    print("---")
    print(f"MATRIX: {ideas_clean}/{len(ideas_seen)} idea(s) traced clean, "
          f"{total_checked - failures}/{total_checked} line(s) confirmed")
    if failures:
        print(f"{failures} problem(s) found across {len(blocks)} claim(s), {total_checked} line(s) checked.")
        return 1, failures, total_checked, len(blocks)

    print(f"All {len(blocks)} claim(s) verified: {total_checked} line(s) checked, all confirmed.")
    return 0, failures, total_checked, len(blocks)


REACTION_PHRASES = [
    "within a minute", "within minutes", "visibly", "surprised", "whole room",
    "the room", "everyone", "nodding", "gasped", "laughed", "applause",
    "at the same time", "almost the same thing",
]

NUMBER_WORDS = {"two": 2, "both": 2, "three": 3, "four": 4, "five": 5}
COUNT_PEOPLE = re.compile(
    r"\b(two|both|three|four|five|several|multiple|many|most|few|all|every)"
    r"\s+(?:different\s+|of\s+the\s+)?(attendees?|people|participants?|members?|clients?)\b",
    re.IGNORECASE,
)

SPEAKER_LABEL = re.compile(r"^([A-Z][A-Z0-9 ]+):")


def speaker_of(quote, transcript_lines):
    """Speaker label of the transcript line holding the start of quote."""
    q = normalise(quote)[:20]
    for i in range(len(transcript_lines)):
        if q in normalise(transcript_lines[i]):
            for j in range(i, -1, -1):
                m = SPEAKER_LABEL.match(transcript_lines[j])
                if m:
                    return m.group(1)
            return None
    return None


def menu_prose(menu_text):
    """Menu text with Source lines (verbatim quotes, already checked) removed."""
    keep = []
    in_not_used = False
    for line in menu_text.splitlines():
        s = line.strip()
        if s.startswith("**NOT USED**"):
            in_not_used = True
            continue
        if in_not_used:
            continue
        if s.startswith("**Source:**") or s.lower().startswith("also shaped by"):
            continue
        keep.append(line)
    return "\n".join(keep)


def check_menu(menu_path, sources_path, transcript_path):
    """Returns the number of menu problems found. See the docstring for the
    two rules and their stated limit."""
    for path in (menu_path, sources_path, transcript_path):
        if not path.exists():
            print(f"File not found: {path}")
            return 1000
    sources_text = sources_path.read_text(encoding="utf-8")
    transcript_lines = transcript_path.read_text(encoding="utf-8").splitlines()
    prose = menu_prose(menu_path.read_text(encoding="utf-8"))
    prose_norm = normalise(prose)

    quotes = [m.group(1) for m in re.finditer(r'(?:SOURCE|NOTES):\s*"([^"]+)"', sources_text)]
    quote_norm = normalise(" ".join(quotes))

    print("MENU CHECK: " + str(menu_path))
    problems = 0

    menu_text = menu_path.read_text(encoding="utf-8")
    slots = re.findall(r"^\*\*IDEA (\d+)\*\*\s*$", menu_text, re.MULTILINE)
    if slots != ["1", "2", "3", "4", "5"]:
        problems += 1
        print(f"  FAIL  expected exactly five slots IDEA 1 to IDEA 5 in order, found: {', '.join(slots) or 'none'}")
    else:
        print("  PASS  five slots found")
        parts = re.split(r"^\*\*IDEA \d+\*\*\s*$", menu_text, flags=re.MULTILINE)[1:]
        seen_gap = False
        for n, body in enumerate(parts, start=1):
            has_title = "**Title:**" in body
            is_gap = "**No idea:**" in body
            if has_title == is_gap:
                problems += 1
                print(f"  FAIL  IDEA {n} is neither a full idea nor a marked gap (or is both)")
            elif is_gap:
                seen_gap = True
            elif seen_gap:
                problems += 1
                print(f"  FAIL  IDEA {n} is a full idea placed after a marked gap, ideas go first")

    transcript_norm = normalise(" ".join(transcript_lines))
    nu = re.search(r"\*\*NOT USED\*\*(.*)", menu_text, re.DOTALL)
    if nu is None:
        problems += 1
        print("  FAIL  no NOT USED list found")
    else:
        for item in re.finditer(r'^-\s+(.+?):\s*"([^"]+)"\s*\(line\s+(\d+)\)', nu.group(1), re.MULTILINE):
            ok, detail = check_source(item.group(2), "line " + item.group(3), transcript_lines, transcript_norm)
            short = item.group(2)[:50] + ("..." if len(item.group(2)) > 50 else "")
            if ok:
                print(f'  PASS  NOT USED "{short}" ({detail})')
            else:
                problems += 1
                print(f'  FAIL  NOT USED "{short}": {detail}')

    for phrase in REACTION_PHRASES:
        pat = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pat, prose_norm):
            if re.search(pat, quote_norm):
                print(f'  PASS  "{phrase}" appears inside a verified quote')
            else:
                problems += 1
                print(f'  FAIL  menu says "{phrase}" but no verified SOURCE/NOTES quote contains it')

    claims = [(m.group("claim"), m.group("lines")) for m in BLOCK.finditer(sources_text)]
    seen = set()
    for m in COUNT_PEOPLE.finditer(prose):
        phrase = normalise(m.group(0))
        if phrase in seen:
            continue
        seen.add(phrase)
        match = [c for c in claims if phrase in normalise(c[0])]
        if not match:
            problems += 1
            print(f'  FAIL  menu says "{phrase}" but no CLAIM in the sources file uses that wording')
            continue
        needed = NUMBER_WORDS.get(phrase.split()[0], 2)
        speakers = set()
        for claim, lines in match:
            for s in SOURCE_LINE.finditer(lines):
                sp = speaker_of(s.group("quote"), transcript_lines)
                if sp:
                    speakers.add(sp)
        if len(speakers) >= needed:
            print(f'  REVIEW "{phrase}": claim has quotes from {len(speakers)} speaker(s) '
                  f'({", ".join(sorted(speakers))}). Read them: do they all do what the claim says?')
        else:
            problems += 1
            print(f'  FAIL  menu says "{phrase}" but its claim is quoted from only '
                  f'{len(speakers)} speaker(s) ({", ".join(sorted(speakers)) or "none found"})')

    print("---")
    if problems:
        print(f"MENU: {problems} problem(s) found in the menu text.")
    else:
        print("MENU: no invented reaction, timing or count words found. REVIEW lines still need a human read.")
    return problems


def selftest():
    """Runs this script against its own two shipped fixtures and reports
    whether the checker's basic logic holds: a correct sources file must
    pass in full, and the deliberately broken one must fail on every line.
    See the module docstring, "What --selftest actually proves," for what
    a pass here does and doesn't establish."""

    verify_dir = Path(__file__).resolve().parent
    transcript_path = verify_dir.parent / "sample" / "transcript.txt"
    notes_path = verify_dir.parent / "sample" / "notes.txt"
    correct_path = verify_dir / "test-cases" / "correct-sources.txt"
    broken_path = verify_dir / "test-cases" / "broken-sources.txt"

    print("=" * 60)
    print("SELFTEST 1 of 4: correct-sources.txt must pass in full")
    print("=" * 60)
    code1, failures1, checked1, blocks1 = run_check(correct_path, transcript_path, notes_path)
    test1_ok = code1 == 0 and failures1 == 0

    print()
    print("=" * 60)
    print("SELFTEST 2 of 4: broken-sources.txt must fail on every line")
    print("=" * 60)
    code2, failures2, checked2, blocks2 = run_check(broken_path, transcript_path, None)
    # Every single SOURCE line in this fixture is deliberately wrong, so a
    # correct checker fails all of them, not just some.
    test2_ok = code2 == 1 and failures2 is not None and checked2 is not None and failures2 == checked2

    print()
    print("=" * 60)
    print("SELFTEST 3 of 4: the shipped sample menu must pass the menu check")
    print("=" * 60)
    sample_dir = verify_dir.parent / "sample"
    test3_ok = check_menu(sample_dir / "expected-output-menu.txt",
                          sample_dir / "expected-output-sources.txt", transcript_path) == 0

    print()
    print("=" * 60)
    print("SELFTEST 4 of 4: broken-menu.txt (invented reaction, timing, count) must fail")
    print("=" * 60)
    broken_problems = check_menu(verify_dir / "test-cases" / "broken-menu.txt",
                                 verify_dir / "test-cases" / "broken-menu-sources.txt", transcript_path)
    test4_ok = broken_problems >= 5  # slots, timing, reaction and room phrases at minimum

    print()
    print("=" * 60)
    print("SELFTEST RESULT")
    print("=" * 60)
    print(("PASS" if test3_ok else "FAIL") + "  sample menu passes the menu check")
    print(("PASS" if test4_ok else "FAIL") + f"  broken-menu.txt: {broken_problems} problem(s) caught")
    if test1_ok:
        print(f"PASS  correct-sources.txt: {checked1} line(s) across {blocks1} claim(s), 0 failures, as expected")
    else:
        print(f"FAIL  correct-sources.txt should have passed cleanly but did not "
              f"({failures1} failure(s) found)")

    if test2_ok:
        print(f"PASS  broken-sources.txt: {failures2} of {checked2} line(s) failed, "
              f"all of them, as expected")
    else:
        found = failures2 if failures2 is not None else "an error occurred"
        total = checked2 if checked2 is not None else "?"
        print(f"FAIL  broken-sources.txt should have failed every line but only "
              f"{found} of {total} failed")

    if test1_ok and test2_ok and test3_ok and test4_ok:
        print()
        print("Selftest passed: this checker correctly passes real grounding "
              "and correctly rejects fabricated or altered quotes.")
        return 0

    print()
    print("Selftest FAILED: this checker's logic does not behave as documented. "
          "Do not trust its verdicts on real output until this is fixed.")
    return 1


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())

    args = sys.argv[1:]
    menu_path = None
    if "--menu" in args:
        i = args.index("--menu")
        if i + 1 >= len(args):
            print("--menu needs a menu file path")
            sys.exit(2)
        menu_path = Path(args[i + 1])
        del args[i:i + 2]
    sys.argv = [sys.argv[0]] + args

    if len(sys.argv) not in (3, 4):
        print("Usage: python check.py <sources-file.txt> <transcript-file.txt> [notes-file.txt] [--menu <menu-file.txt>]")
        print("       python check.py --selftest")
        sys.exit(2)

    sources_path = Path(sys.argv[1])
    transcript_path = Path(sys.argv[2])
    notes_path = Path(sys.argv[3]) if len(sys.argv) == 4 else None

    exit_code, _, _, _ = run_check(sources_path, transcript_path, notes_path)
    if menu_path is not None:
        print()
        if check_menu(menu_path, sources_path, transcript_path):
            exit_code = exit_code or 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
