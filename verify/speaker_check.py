#!/usr/bin/env python3
"""
Independent speaker/count/attribution checker for the Lead Magnet Translator.

Optional, and separate from check.py. A real translation runs entirely
inside a Claude Project chat and never calls this script. This exists so a
skeptical reader (a competition judge, or Yasuko spot-checking a menu) can
mechanically reproduce PART of rules.md section 7b's independent
interpretive recheck, the part that's genuinely mechanical: which speaker
said each SOURCE quote, how many distinct speakers back a claim, and
whether a claim's own stated count or host/attendee attribution matches
that mapping.

This script cannot fully check whether a quote actually supports the
strength or characterisation a claim gives it (section 7b step 3: "the
comparison worked," "the room reacted well", etc.). That is a judgement
call about meaning, not a structural fact, and stays a required manual
recheck every time (rules.md section 7b), whether or not this script ran
and whether or not it passed. A clean run of this script is not a
substitute for that step.

It does, however, print REVIEW flags nominating a claim for closer
attention during that manual step: an absolute word ("everyone", "always"),
a characterisation word sitting near a negation or contrast word in its own
source quote, an unusually short/isolated source quote, or a claim whose
SOURCE line numbers sit far outside every other claim filed under the same
IDEA (a cheap signal a claim may have been filed under the wrong idea --
see flag_idea_outliers). These are cheap, purely structural signals, not
verdicts -- they narrow what a human looks at first during step 3, they
never replace doing step 3. A REVIEW flag never affects this script's
PASS/FAIL exit code.

Usage:
    python speaker_check.py <sources-file.txt> <transcript-file.txt>
    python speaker_check.py --selftest

What it checks, per IDEA/CLAIM block in the sources file:
  1. Speaker mapping: for every SOURCE line, which transcript speaker's
     turn the quote falls inside (using the same line-window/fallback
     logic as check.py). A quote that cannot be matched to a turn is
     reported as UNRESOLVED, not silently skipped.
  2. Distinct-speaker count: how many different speakers back this claim's
     SOURCE lines.
  3. Numeric-word mismatch: if the CLAIM text names an exact count with a
     number word ("two attendees", "three separate times"), flags a
     mismatch against the distinct-speaker count actually found. Vague
     words ("some", "several", "many") are never flagged, since rules.md
     section 7 step 5 allows those deliberately when a transcript doesn't
     make a count exact.
  4. Host/attendee attribution: if the CLAIM text names an attribution
     ("the host said", "an attendee suggested", "the coach explained"),
     flags a mismatch against the actual speaker(s) found -- but ONLY when
     this script can tell, with reasonable confidence, which transcript
     labels are the host versus attendees (see classify_speakers below). If
     it can't tell confidently, it says so plainly and skips this check
     rather than guessing. A wrong guess here would be worse than no check
     at all.

This script assumes the transcript marks speaker turns with a label at the
start of a line, followed by a colon (e.g. "COACH A:", "ATTENDEE 1:",
"Host:", "Jane:"). If the transcript doesn't follow this pattern at all, it
says so and exits without guessing at turn boundaries.

This is a first pass at the mechanical half of section 7b. It is new,
built under deadline pressure, and has not yet been proven against a
transcript these rules haven't seen (see rules.md section 7b and the
handoff notes for the open item on testing against an unseen transcript).
Treat a clean run as useful evidence, not as proof the mapping is perfect
-- spot-check its speaker assignments against the transcript yourself,
especially the first few times you use it.
"""

import re
import sys
from pathlib import Path

LINE_WINDOW = 3  # matches check.py's window for "around line N" references

BLOCK = re.compile(
    r'IDEA:\s*(?P<idea>.+?)\s*\n'
    r'CLAIM:\s*(?P<claim>.+?)\s*\n'
    r'(?P<lines>(?:(?:SOURCE|NOTES):.*\n?)+)',
)

SOURCE_LINE = re.compile(
    r'SOURCE:\s*"(?P<quote>[^"]+)"\s*—\s*(?P<ref>.+)',
)

LINE_NUMBER = re.compile(r'line\s+(\d+)', re.IGNORECASE)

# A speaker-turn label: start of line, a short run of 1-4 words, each
# starting with a capital letter (a name, a role, or a numbered role like
# "Attendee 1"), optionally followed by a parenthetical (e.g. a username,
# as Zoom's VTT export produces: "Jane Smith (jane-s):"), ending in a
# colon, followed by actual dialogue on the same line. Anchored to
# line-start and requires capitalised words so it doesn't match a colon
# inside a lowercase sentence, or a metadata line like "Session: ..."
# (also excluded by name below).
SPEAKER_LABEL = re.compile(
    r"^((?:[A-Z][A-Za-z'.]*\s*){1,4}\d{0,2}(?:\s*\([^)]*\))?):\s+(\S.*)$"
)

# A second, common transcript shape (Otter.ai and similar auto-transcripts):
# the speaker label sits alone on its own line, followed by a timestamp,
# with NO colon at all -- e.g. "YO  26:04" or "Speaker 3  36:23". The
# dialogue itself starts on the line(s) after. Initials or a short name
# (which can itself include a trailing number, e.g. "Speaker 3"), two-plus
# spaces, then a timestamp (M:SS, MM:SS, or H:MM:SS).
SPEAKER_LABEL_TIMESTAMP = re.compile(
    r"^([A-Za-z][A-Za-z0-9' .]{0,30}?)\s{2,}(\d{1,2}:\d{2}(?::\d{2})?)\s*$"
)

# A third, common transcript shape (Fathom and similar auto-transcripts):
# the timestamp comes FIRST, then a dash, then the label, alone on its own
# line -- e.g. "0:04 - DH" or "12:37 - Dana Price". Dialogue starts on the
# line(s) after, often indented.
SPEAKER_LABEL_TIMESTAMP_FIRST = re.compile(
    r"^(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([A-Za-z][A-Za-z0-9' .]{0,30}?)\s*$"
)

# Header/metadata lines that happen to match the label pattern but aren't
# a speaker turn. Checked case-insensitively against the label text.
NON_SPEAKER_LABELS = {
    "host", "session", "date", "attendees present in this excerpt",
    "attendee list", "topic", "location", "duration",
}

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
VAGUE_COUNT_WORDS = {"some", "several", "many", "a few", "multiple"}

# Attribution phrases, not bare vocabulary words -- a claim can mention
# "a client" or "the coach's approach" without attributing the QUOTE
# itself to that person. Only phrases that plausibly precede or follow a
# reported statement count (word chosen + said/asked/suggested/named/
# raised/pointed out/flagged, in either order, within a few words).
_ATTR_VERBS = r"(?:said|asked|suggested|named|raised|pointed out|flagged|noted|explained|shared|mentioned)"
HOST_ATTRIBUTION_PATTERNS = [
    re.compile(rf"\b(?:the\s+)?(?:host|coach|facilitator|presenter)\b.{{0,25}}\b{_ATTR_VERBS}\b", re.IGNORECASE),
    re.compile(rf"\b{_ATTR_VERBS}\b.{{0,25}}\b(?:the\s+)?(?:host|coach|facilitator|presenter)\b", re.IGNORECASE),
]
ATTENDEE_ATTRIBUTION_PATTERNS = [
    re.compile(rf"\b(?:an?\s+)?(?:attendee|participant|member)\b.{{0,25}}\b{_ATTR_VERBS}\b", re.IGNORECASE),
    re.compile(rf"\b{_ATTR_VERBS}\b.{{0,25}}\b(?:an?\s+)?(?:attendee|participant|member)\b", re.IGNORECASE),
]

# --- Characterisation-risk flags -------------------------------------
# None of these prove a claim overstates its source. They are cheap,
# purely structural signals that nominate a claim for closer attention
# during the required manual section 7b step 3 recheck -- they narrow
# what a human has to look at first, they never replace looking.

ABSOLUTE_WORDS = re.compile(
    r"\b(?:everyone|everybody|always|never|all of (?:them|the|us)|"
    r"nobody|no one|entirely|completely|totally|undeniably|obviously|"
    r"clearly (?:shows|proves|demonstrates)|proves|definitively)\b",
    re.IGNORECASE,
)

NEGATION_CONTRAST_WORDS = re.compile(
    r"\b(?:not|n't|but|however|although|though|except|despite|"
    r"struggled|failed|didn't|couldn't|wasn't|weren't)\b",
    re.IGNORECASE,
)

# Characterisation verbs the claim might be resting on: "the comparison
# worked", "the room reacted well", "everyone agreed". Deliberately a
# looser net than the attribution verbs above -- this is a nomination for
# review, not a verdict, so a wider net costs a false positive, not a
# missed real one.
CHARACTERIZATION_WORDS = re.compile(
    r"\b(?:worked|working|works|reacted|reaction|agreed|agreement|"
    r"resonated|landed|succeeded|success|improved|improvement|"
    r"loved|hated|excited|impressed|convinced|proved|proof)\b",
    re.IGNORECASE,
)

SHORT_QUOTE_WORD_THRESHOLD = 6  # a quote at or under this many words is
                                 # flagged as possibly too short/isolated
                                 # to carry a claim's full weight on its
                                 # own -- a proxy, not a measurement.

# An idea's claims are almost always grounded in one contiguous stretch of
# the conversation -- the moment that idea came up. A claim whose SOURCE
# line numbers sit far outside the range every OTHER claim under the same
# IDEA uses is a cheap, purely structural signal that it may have been
# filed under the wrong idea (e.g. a claim moved to a different IDEA
# heading than the one its quote actually supports), the class of error
# neither this script's speaker/count checks nor check.py's quote-exists
# check can see: both operate one claim at a time and never compare a
# claim's placement against its own idea's other claims. Like the other
# risk flags, this is a nomination for the manual recheck, not a verdict --
# a genuinely later callback to an earlier idea is real and legitimate.
IDEA_OUTLIER_LINE_GAP = 200  # a claim's nearest SOURCE line is flagged if
                              # it falls this many lines outside the range
                              # spanned by its own idea's other claims.


def flag_characterization_risk(claim_text, source_quotes):
    """Returns a list of short, human-readable flags (possibly empty).
    Each flag names WHY a claim was nominated for closer attention during
    the required section 7b step 3 recheck. This never fails the run
    (main() does not count these toward the exit code) -- they are
    nominations, not findings, since none of them can tell whether the
    transcript actually supports or contradicts the characterisation."""
    flags = []

    if ABSOLUTE_WORDS.search(claim_text):
        word = ABSOLUTE_WORDS.search(claim_text).group(0)
        flags.append(
            f'uses an absolute word ("{word}") -- rules.md section 7 step 5 '
            f"says count what's countable; confirm the transcript really "
            f"supports this absolute, not just a strong instance of it"
        )

    if CHARACTERIZATION_WORDS.search(claim_text):
        char_word = CHARACTERIZATION_WORDS.search(claim_text).group(0)
        # Only worth flagging the negation/contrast check when there's a
        # characterisation word for it to be undercutting in the first
        # place -- otherwise "not" appearing anywhere is much too broad.
        nearby_negation = any(
            NEGATION_CONTRAST_WORDS.search(q) for q in source_quotes
        )
        if nearby_negation:
            flags.append(
                f'characterises the quote as "{char_word}", but a negation or '
                f'contrast word (e.g. "not", "but", "however") appears in one '
                f"of its own SOURCE quotes -- check the transcript doesn't "
                f"actually hedge or contradict this characterisation nearby"
            )

    if source_quotes:
        shortest = min(source_quotes, key=lambda q: len(q.split()))
        if len(shortest.split()) <= SHORT_QUOTE_WORD_THRESHOLD:
            flags.append(
                f'shortest SOURCE quote is only {len(shortest.split())} word(s) '
                f'("{shortest.strip()}") -- a short, isolated fragment can be '
                f"real and still not carry the full weight of the claim built "
                f"on it; read it in context, not just on its own"
            )

    return flags


def normalise(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_turns(transcript_lines):
    """Returns a list of (start_line_idx, end_line_idx, label, text) turns,
    0-indexed line positions inclusive. A turn runs from its label line to
    the line before the next label line (or end of file).

    Tries three label shapes on each line, in order:
      1. "LABEL: dialogue text" on one line (SPEAKER_LABEL) -- also covers
         Zoom VTT's "Name (username): text".
      2. "LABEL  MM:SS" alone on its own line, no colon, dialogue starting
         on the line(s) after (SPEAKER_LABEL_TIMESTAMP) -- the shape
         Otter.ai and similar auto-transcripts produce.
      3. "MM:SS - LABEL" alone on its own line, timestamp FIRST, dialogue
         starting the line(s) after (SPEAKER_LABEL_TIMESTAMP_FIRST) -- the
         shape Fathom and similar auto-transcripts produce.
    A transcript is assumed to use ONE shape consistently throughout, so
    once any shape has matched at least once, only that shape is tried
    for the rest of the file; this avoids a stray line coincidentally
    matching a different pattern and splitting a turn in the wrong place."""
    turns = []
    current = None
    shape_locked = None  # None, "inline", "timestamp", or "timestamp_first"

    for i, line in enumerate(transcript_lines):
        stripped = line.strip()
        label = None
        dialogue_on_same_line = None
        matched_shape = None

        if shape_locked in (None, "inline"):
            m = SPEAKER_LABEL.match(stripped)
            if m and m.group(1).strip().lower() not in NON_SPEAKER_LABELS:
                # Drop a trailing "(username)" parenthetical from the
                # displayed label (Zoom VTT exports add one), so the same
                # person's turns group under one clean name rather than a
                # label cluttered with their username on every line.
                raw_label = m.group(1).strip()
                label = re.sub(r'\s*\([^)]*\)\s*$', '', raw_label).strip()
                dialogue_on_same_line = m.group(2)
                matched_shape = "inline"

        if label is None and shape_locked in (None, "timestamp"):
            m = SPEAKER_LABEL_TIMESTAMP.match(stripped)
            if m and m.group(1).strip().lower() not in NON_SPEAKER_LABELS:
                label = m.group(1).strip()
                dialogue_on_same_line = None  # dialogue starts next line
                matched_shape = "timestamp"

        if label is None and shape_locked in (None, "timestamp_first"):
            m = SPEAKER_LABEL_TIMESTAMP_FIRST.match(stripped)
            if m and m.group(2).strip().lower() not in NON_SPEAKER_LABELS:
                label = m.group(2).strip()
                dialogue_on_same_line = None  # dialogue starts next line
                matched_shape = "timestamp_first"

        if label is not None:
            if shape_locked is None:
                shape_locked = matched_shape
            if current is not None:
                current["end"] = i - 1
                turns.append(current)
            current = {
                "start": i,
                "end": None,
                "label": label,
                "text_lines": [dialogue_on_same_line] if dialogue_on_same_line else [],
            }
        elif current is not None:
            current["text_lines"].append(line)

    if current is not None:
        current["end"] = len(transcript_lines) - 1
        turns.append(current)
    return turns


def find_turn_for_line(turns, line_idx):
    for t in turns:
        if t["start"] <= line_idx <= t["end"]:
            return t
    return None


def locate_quote_turn(quote, ref, transcript_lines, turns, full_text_normalised):
    """Mirrors check.py's check_source logic to find WHERE a quote is,
    then maps that location to a speaker turn. Returns (turn_or_None,
    detail_string)."""
    quote_norm = normalise(quote)

    m = LINE_NUMBER.search(ref)
    candidate_lines = None
    if m:
        line_no = int(m.group(1))
        window_start = max(0, line_no - 1 - LINE_WINDOW)
        window_end = min(len(transcript_lines), line_no + LINE_WINDOW)
        window_text = normalise(" ".join(transcript_lines[window_start:window_end]))
        if quote_norm in window_text:
            candidate_lines = range(window_start, window_end)

    if candidate_lines is None:
        if quote_norm not in full_text_normalised:
            return None, "quote not found in transcript at all (check.py would also fail this)"
        # Fall back to scanning every turn for the quote, since we don't
        # have a reliable line anchor.
        for t in turns:
            turn_text = normalise(" ".join(
                [transcript_lines[i] for i in range(t["start"], t["end"] + 1)]
            ))
            if quote_norm in turn_text:
                return t, "found by full-transcript scan (no reliable line anchor)"
        return None, "quote found in transcript but couldn't be matched to a single speaker turn"

    # We have a plausible line window; find which turn(s) it overlaps.
    matched_turns = []
    for t in turns:
        if any(t["start"] <= i <= t["end"] for i in candidate_lines):
            matched_turns.append(t)

    if len(matched_turns) == 1:
        return matched_turns[0], f"matched via line reference"
    if len(matched_turns) > 1:
        # Narrow to whichever turn actually contains the quote text.
        for t in matched_turns:
            turn_text = normalise(" ".join(
                [transcript_lines[i] for i in range(t["start"], t["end"] + 1)]
            ))
            if quote_norm in turn_text:
                return t, "matched via line reference, narrowed among overlapping turns"
        return None, "line reference spans more than one speaker turn and the quote text didn't narrow it"

    return None, "line reference didn't fall inside any recognised speaker turn"


def classify_speakers(turns):
    """Best-effort, conservative classification of which speaker labels
    are 'the host' versus 'attendees'. Returns (host_labels_set,
    attendee_labels_set, confident_bool).

    Heuristic: if exactly one distinct label appears meaningfully more
    often than any other AND every other label matches a numbered/lettered
    pattern suggesting multiple interchangeable participants (e.g.
    "Attendee 1", "Attendee 2", "Speaker 3"), call the frequent one the
    host. Otherwise, not confident -- don't guess.
    """
    from collections import Counter
    counts = Counter(t["label"] for t in turns)
    if len(counts) < 2:
        return set(), set(), False

    ranked = counts.most_common()
    top_label, top_count = ranked[0]
    others = ranked[1:]

    # Confidence signal 1: the top label clearly dominates turn count.
    dominates = all(top_count > c for _, c in others) and top_count >= 2

    # Confidence signal 2: the other labels look like a numbered/lettered
    # participant series (share a common word stem, differ by a trailing
    # number), which suggests they're interchangeable non-host speakers.
    other_labels = [lbl for lbl, _ in others]
    stems = set()
    for lbl in other_labels:
        stem = re.sub(r'\s*\d+\s*$', '', lbl).strip().lower()
        stems.add(stem)
    participant_series = len(stems) == 1 and len(other_labels) >= 1

    if dominates and participant_series:
        return {top_label}, set(other_labels), True

    return set(), set(), False


def extract_claim_count(claim_text):
    """Returns an int if the claim names an exact number word, else None.
    Deliberately ignores vague words (some/several/many), which are always
    acceptable per rules.md section 7 step 5."""
    claim_lower = claim_text.lower()
    for vague in VAGUE_COUNT_WORDS:
        if vague in claim_lower:
            return None  # vague language present; nothing to flag
    for word, value in NUMBER_WORDS.items():
        if re.search(r'\b' + word + r'\b', claim_lower):
            return value
    return None


def extract_source_line_numbers(block_lines):
    """Returns a list of ints: every line number named in this block's
    SOURCE references (e.g. "around line 1245" -> 1245). Lines with no
    number at all are skipped -- nothing to compare for those."""
    numbers = []
    for s in SOURCE_LINE.finditer(block_lines):
        ref = s.group("ref").strip()
        m = LINE_NUMBER.search(ref)
        if m:
            numbers.append(int(m.group(1)))
    return numbers


def flag_idea_outliers(idea_line_numbers):
    """idea_line_numbers: {idea_name: [(block_index, [line_numbers]), ...]}.
    Returns {block_index: flag_string} for any block whose own line numbers
    fall entirely outside IDEA_OUTLIER_LINE_GAP of every OTHER block's line
    numbers under the same idea. An idea with only one block, or a block
    with no line numbers at all, is never flagged -- there's nothing to
    compare it against."""
    flags = {}
    for idea, blocks in idea_line_numbers.items():
        if len(blocks) < 2:
            continue
        for i, (block_idx, my_lines) in enumerate(blocks):
            if not my_lines:
                continue
            other_lines = [
                n for j, (_, lines) in enumerate(blocks) if j != i for n in lines
            ]
            if not other_lines:
                continue
            closest_gap = min(
                abs(mine - other) for mine in my_lines for other in other_lines
            )
            if closest_gap > IDEA_OUTLIER_LINE_GAP:
                flags[block_idx] = (
                    f'this claim\'s SOURCE line(s) ({min(my_lines)}-{max(my_lines)}) sit '
                    f'{closest_gap} lines from every other claim filed under the same '
                    f'IDEA ("{idea}") -- worth confirming this claim is actually about '
                    f"that idea, not a different one filed here by mistake"
                )
    return flags


def extract_claim_attribution(claim_text):
    """Returns 'host', 'attendee', or None -- only when the claim actually
    attributes a reported statement to one ("the host explained...", "an
    attendee asked..."), not just mentions a related word in passing (e.g.
    "what a client reacts to" is not an attribution to an attendee)."""
    if any(p.search(claim_text) for p in HOST_ATTRIBUTION_PATTERNS):
        return "host"
    if any(p.search(claim_text) for p in ATTENDEE_ATTRIBUTION_PATTERNS):
        return "attendee"
    return None


def run_check(sources_path, transcript_path):
    if not sources_path.exists():
        print(f"Sources file not found: {sources_path}")
        return 2
    if not transcript_path.exists():
        print(f"Transcript file not found: {transcript_path}")
        return 2

    sources_text = sources_path.read_text(encoding="utf-8")
    transcript_lines = transcript_path.read_text(encoding="utf-8").splitlines()
    full_text_normalised = normalise(" ".join(transcript_lines))

    turns = parse_turns(transcript_lines)
    if not turns:
        print("Could not find any speaker-labelled turns in this transcript")
        print('(expected a pattern like "SPEAKER: text" at the start of lines).')
        print("This script can't map quotes to speakers without that. Nothing")
        print("checked. rules.md section 7b's speaker mapping still needs to be")
        print("done by hand for this transcript.")
        return 2

    host_labels, attendee_labels, attribution_confident = classify_speakers(turns)
    if attribution_confident:
        print(f"Host/attendee attribution: confident. Treating {sorted(host_labels)} "
              f"as host, {sorted(attendee_labels)} as attendees.")
    else:
        print("Host/attendee attribution: NOT confident from this transcript's speaker "
              "labels alone. Skipping the attribution mismatch check rather than "
              "guessing. Check host-vs-attendee claims by hand per rules.md section 7b "
              "step 2.")
    print()

    blocks = list(BLOCK.finditer(sources_text))
    if not blocks:
        print(f"No IDEA/CLAIM/SOURCE blocks found in {sources_path}")
        return 2

    # First pass: gather each block's own SOURCE line numbers, grouped by
    # idea, so flag_idea_outliers can compare a block against its idea's
    # other blocks before any output is printed.
    idea_line_numbers = {}
    for block_idx, block_match in enumerate(blocks):
        idea = block_match.group("idea").strip()
        block_lines = block_match.group("lines")
        line_numbers = extract_source_line_numbers(block_lines)
        idea_line_numbers.setdefault(idea, []).append((block_idx, line_numbers))
    outlier_flags = flag_idea_outliers(idea_line_numbers)

    problems = 0
    checked_claims = 0
    total_risk_flags = 0

    for block_idx, block_match in enumerate(blocks):
        idea = block_match.group("idea").strip()
        claim = block_match.group("claim").strip()
        block_lines = block_match.group("lines")
        source_lines = list(SOURCE_LINE.finditer(block_lines))
        if not source_lines:
            continue  # check.py already flags NOTES-only blocks as a failure

        checked_claims += 1
        print(f"[{idea}] {claim}")

        speakers_found = []
        for s in source_lines:
            quote = s.group("quote")
            ref = s.group("ref").strip()
            turn, detail = locate_quote_turn(quote, ref, transcript_lines, turns, full_text_normalised)
            short_quote = quote[:55] + ("..." if len(quote) > 55 else "")
            if turn is None:
                problems += 1
                print(f'  UNRESOLVED  "{short_quote}"')
                print(f"              {detail}")
                continue
            speakers_found.append(turn["label"])
            print(f'  {turn["label"]:<15} "{short_quote}"  ({detail})')

        distinct_speakers = sorted(set(speakers_found))
        print(f"  -> {len(distinct_speakers)} distinct speaker(s): {distinct_speakers}")

        claimed_count = extract_claim_count(claim)
        if claimed_count is not None and speakers_found:
            if claimed_count != len(distinct_speakers):
                problems += 1
                print(f"  MISMATCH  claim names a count of {claimed_count}, but "
                      f"{len(distinct_speakers)} distinct speaker(s) actually back it")
            else:
                print(f"  count OK  claim's number matches {len(distinct_speakers)} distinct speaker(s)")

        if attribution_confident and speakers_found:
            claimed_attribution = extract_claim_attribution(claim)
            if claimed_attribution == "host":
                if not all(lbl in host_labels for lbl in distinct_speakers):
                    problems += 1
                    print(f"  MISMATCH  claim attributes this to the host, but speaker(s) "
                          f"found were {distinct_speakers}")
            elif claimed_attribution == "attendee":
                if not all(lbl in attendee_labels for lbl in distinct_speakers):
                    problems += 1
                    print(f"  MISMATCH  claim attributes this to an attendee, but speaker(s) "
                          f"found were {distinct_speakers}")

        source_quote_texts = [s.group("quote") for s in source_lines]
        risk_flags = flag_characterization_risk(claim, source_quote_texts)
        for flag in risk_flags:
            total_risk_flags += 1
            print(f"  REVIEW    {flag}")

        if block_idx in outlier_flags:
            total_risk_flags += 1
            print(f"  REVIEW    {outlier_flags[block_idx]}")

        print()

    print("---")
    if total_risk_flags:
        print(f"{total_risk_flags} claim(s) flagged for closer attention during the required")
        print("section 7b step 3 recheck (absolute wording, a characterisation word sitting")
        print("near a negation/contrast word in its own source, or an unusually short source")
        print("quote). A flag here is a NOMINATION for review, not a verdict -- none of these")
        print("checks can tell whether the transcript actually supports the characterisation.")
        print("It does not affect this script's PASS/FAIL result below.")
        print()

    if problems:
        print(f"{problems} issue(s) found across {checked_claims} claim(s) checked.")
        print("This covers only the mechanical part of rules.md section 7b (mapping,")
        print("counts, attribution). Characterisation claims (\"the comparison worked\",")
        print("\"the room reacted well\") are NOT checked here and still need the manual")
        print("recheck in section 7b step 3, every time, regardless of this result.")
        return 1

    print(f"No count or attribution mismatches found across {checked_claims} claim(s).")
    print("This covers only the mechanical part of rules.md section 7b (mapping,")
    print("counts, attribution). Characterisation claims still need the manual")
    print("recheck in section 7b step 3 -- this is not a substitute for it.")
    return 0


def selftest():
    """Runs this script against six shipped fixtures: a known-good
    sources file (must pass clean), the shared broken-sources.txt fixture
    (every quote invented/altered, must fail), a dedicated fixture with
    real quotes but a wrong claimed count and a wrong host/attendee
    attribution (must fail on exactly those two grounds, the class of
    error check.py cannot see at all), and three fixtures in the OTHER
    supported label shapes: Otter.ai-style "LABEL  MM:SS" on its own line
    with no colon, Zoom VTT-style "Name (username): text" with a sequence
    number and timestamp range on the lines before it, and Fathom-style
    "MM:SS - LABEL" (timestamp first) on its own line -- to prove all four
    shapes work, not just the one the original fixtures happen to use."""

    verify_dir = Path(__file__).resolve().parent
    transcript_path = verify_dir.parent / "sample" / "transcript.txt"
    correct_path = verify_dir / "test-cases" / "correct-sources.txt"
    broken_path = verify_dir / "test-cases" / "broken-sources.txt"
    mismatch_path = verify_dir / "test-cases" / "speaker-mismatch-sources.txt"
    timestamp_transcript_path = verify_dir / "test-cases" / "timestamp-format-transcript.txt"
    timestamp_sources_path = verify_dir / "test-cases" / "timestamp-format-sources.txt"
    vtt_transcript_path = verify_dir / "test-cases" / "vtt-format-transcript.txt"
    vtt_sources_path = verify_dir / "test-cases" / "vtt-format-sources.txt"
    fathom_transcript_path = verify_dir / "test-cases" / "fathom-format-transcript.txt"
    fathom_sources_path = verify_dir / "test-cases" / "fathom-format-sources.txt"
    risk_sources_path = verify_dir / "test-cases" / "characterization-risk-sources.txt"
    outlier_transcript_path = verify_dir / "test-cases" / "idea-outlier-transcript.txt"
    outlier_sources_path = verify_dir / "test-cases" / "idea-outlier-sources.txt"

    results = []

    print("=" * 60)
    print("SELFTEST 1 of 4: correct-sources.txt must pass clean")
    print("=" * 60)
    code1 = run_check(correct_path, transcript_path)
    results.append(("correct-sources.txt (expect PASS)", code1 == 0))

    print()
    print("=" * 60)
    print("SELFTEST 2 of 4: broken-sources.txt must fail (quotes unresolved)")
    print("=" * 60)
    code2 = run_check(broken_path, transcript_path)
    results.append(("broken-sources.txt (expect FAIL)", code2 == 1))

    print()
    print("=" * 60)
    print("SELFTEST 3 of 4: speaker-mismatch-sources.txt must fail on a real")
    print("count mismatch and a real attribution mismatch, with every quote")
    print("itself genuine (this is the class check.py alone cannot catch)")
    print("=" * 60)
    code3 = run_check(mismatch_path, transcript_path)
    results.append(("speaker-mismatch-sources.txt (expect FAIL)", code3 == 1))

    print()
    print("=" * 60)
    print("SELFTEST 4 of 5: timestamp-format fixtures must pass clean, using")
    print("a second supported label shape (no colon, label+timestamp on")
    print("its own line, dialogue starting the line after)")
    print("=" * 60)
    code4 = run_check(timestamp_sources_path, timestamp_transcript_path)
    results.append(("timestamp-format-sources.txt (expect PASS)", code4 == 0))

    print()
    print("=" * 60)
    print("SELFTEST 5 of 6: vtt-format fixtures must pass clean, using a")
    print("third supported label shape (Zoom VTT export: sequence number")
    print("and timestamp range before 'Name (username): text')")
    print("=" * 60)
    code5 = run_check(vtt_sources_path, vtt_transcript_path)
    results.append(("vtt-format-sources.txt (expect PASS)", code5 == 0))

    print()
    print("=" * 60)
    print("SELFTEST 6 of 7: fathom-format fixtures must pass clean, using a")
    print("fourth supported label shape (Fathom export: 'MM:SS - LABEL',")
    print("timestamp first, on its own line)")
    print("=" * 60)
    code6 = run_check(fathom_sources_path, fathom_transcript_path)
    results.append(("fathom-format-sources.txt (expect PASS)", code6 == 0))

    print()
    print("=" * 60)
    print("SELFTEST 7 of 7: characterization-risk-sources.txt must still PASS")
    print("(risk flags never affect exit code) but must print exactly 3 REVIEW")
    print("flags -- absolute wording, a negated characterisation, a short quote")
    print("=" * 60)
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code7 = run_check(risk_sources_path, transcript_path)
    captured = buf.getvalue()
    print(captured)
    review_count = captured.count("REVIEW    ")
    results.append(("characterization-risk-sources.txt (expect PASS, exit 0)", code7 == 0))
    results.append((f"characterization-risk-sources.txt (expect 3 REVIEW flags, got {review_count})", review_count == 3))

    print()
    print("=" * 60)
    print("SELFTEST 8 of 8: idea-outlier-sources.txt -- two genuine quotes,")
    print("both real, but filed under the same IDEA despite sitting 225 lines")
    print("apart -- must still PASS (every quote is real, no count/attribution")
    print("mismatch) but print exactly 2 REVIEW flags nominating both claims")
    print("as possibly filed under the wrong idea")
    print("=" * 60)
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        code8 = run_check(outlier_sources_path, outlier_transcript_path)
    captured2 = buf2.getvalue()
    print(captured2)
    outlier_flag_count = captured2.count("filed under the same IDEA")
    results.append(("idea-outlier-sources.txt (expect PASS, exit 0)", code8 == 0))
    results.append((f"idea-outlier-sources.txt (expect 2 outlier REVIEW flags, got {outlier_flag_count})", outlier_flag_count == 2))

    print()
    print("=" * 60)
    print("SELFTEST RESULT")
    print("=" * 60)
    all_ok = True
    for label, ok in results:
        print(("PASS  " if ok else "FAIL  ") + label)
        all_ok = all_ok and ok

    print()
    if all_ok:
        print("Selftest passed: this checker correctly passes clean grounding, "
              "correctly rejects fabricated quotes, and correctly catches a "
              "real count/attribution mismatch even when every quote is genuine.")
        return 0

    print("Selftest FAILED: this checker's logic does not behave as documented. "
          "Do not trust its verdicts until this is fixed.")
    return 1


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())

    if len(sys.argv) != 3:
        print("Usage: python speaker_check.py <sources-file.txt> <transcript-file.txt>")
        print("       python speaker_check.py --selftest")
        sys.exit(2)

    sources_path = Path(sys.argv[1])
    transcript_path = Path(sys.argv[2])
    sys.exit(run_check(sources_path, transcript_path))


if __name__ == "__main__":
    main()
