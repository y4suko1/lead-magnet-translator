# Output Schema

This is the fixed contract every output must follow. Every run produces two things: an ideas menu, and a separate sources file.

## The ideas menu

Between three and five ideas. Fewer is fine if the transcript can't genuinely support more; padding with a weak idea is not.

Each idea has the same seven parts, in this order:

1. **Title**: the name of the lead magnet, specific and punchy.
2. **Format**: what it is (checklist, mini-guide, quiz, template, swipe file, short video script, worksheet, etc.).
3. **Core Problem**: the specific struggle the transcript raised, grounded in an actual moment, not a generic problem.
4. **Microsolution**: the one small, complete win the lead magnet delivers.
5. **Why This Converts**: the grounded business reasoning, tied to what actually happened in the session.
6. **Pitch Line**: one sentence with real energy a business owner could use to introduce it.
7. **Source**: one or two headline transcript quotes with line references, in the fixed format `"[exact quoted fragment]" (line [N])`, joined by ` · ` if two. If a call note also shaped this idea, one short line follows: `Also shaped by your own notes.` (no quote, attribution only, since a reader outside the room can't verify a private note the way they can a transcript line).

Titles and the seven part-labels are bolded, and a divider separates each idea from the next. No em dashes. No `NOTES:` quotes anywhere in the menu, since only a transcript quote is independently checkable by a reader who doesn't have the notes. This is the document a reader picks an idea from, or checks one against, without needing the companion file.

**Both a fidelity bar and a spark bar apply.** An idea that's grounded but flat (generic title, boring angle) fails the spark bar even though it passes fidelity. An idea that's exciting but not traceable to the transcript fails fidelity even though it might read well. Both are required for every idea in the menu.

## The sources file

Named `sources-[YYYY-MM-DD].txt`, delivered alongside the menu, never merged into it. This is where an idea's *full* grounding lives, every claim and quote, not just the one or two headline quotes already shown in the menu's own Source part. One or more blocks per idea, one block per distinct claim:

```
IDEA: [the idea's Title, exactly as it appears in the menu]
CLAIM: [a short label of what the idea is grounded in]
SOURCE: "[exact quoted fragment from the transcript]" — [line reference or approximate location]
```

`CLAIM` is a brief label, not a restatement of the idea's Core Problem or Why This Converts in full. One short phrase or sentence naming what the quote establishes is enough; the reasoning itself lives in the menu, not here.

An idea can have more than one block if more than one distinct claim supports it (e.g. one block for the Core Problem, another for Why This Converts). A quoted fragment must be copied character-for-character from its source, never paraphrased.

**If call notes were supplied alongside the transcript** (see "Optional call notes" below), a block can also carry a `NOTES:` line. Both go under the *same* `CLAIM` whenever a note and a transcript quote support the same single claim together, stacked as separate lines in one block, the same way two `SOURCE:` lines already stack under one claim when two transcript quotes support it:

```
IDEA: [the idea's Title]
CLAIM: [a short label, this one backed by both]
SOURCE: "[exact quoted fragment from the transcript]" — [line reference]
NOTES: "[exact quoted fragment from the business owner's own notes]"
```

Only start a new block, with its own `CLAIM`, when it's genuinely a different claim, not just a different kind of source for the same one. A `NOTES:` line has no line reference, since notes aren't line-numbered the way a transcript is. Every idea still needs at least one `SOURCE:` line somewhere across its block or blocks; a `NOTES:` line can add weight, but never stands alone as an idea's only grounding.

## Optional call notes

If the business owner supplies their own notes from the session alongside the transcript, the tool uses them to shape which ideas surface and how they're framed. Notes are optional; if none are given, the tool works exactly as it would from the transcript alone. See `rules.md` section 3.

## Checking this yourself

You don't need to take the output's word for it. Open the sources file, find the `SOURCE:` line you want to check, then open the transcript at the line given and confirm the quoted words actually appear there. For a `NOTES:` line, check it against the notes you supplied instead.

If you'd rather not do this by hand for every idea, `verify/` has an optional script that does it for you. See `verify/README.md`. You never need to run it to get a menu from this tool; it's there only if you want to double-check mechanically.

## What the spark check looks like, since it isn't mechanically checkable

Unlike the grounding (which a script can verify), whether an idea is genuinely fun and engaging is a judgement call. The tool makes that call as part of its own self-check (see `rules.md` section 7), and a human reader should make the same call before using an idea: would a business owner actually want to build this, and would a lead actually want to opt in for it. A grounded idea that reads flat isn't a finished output; it's a signal to sharpen the title and pitch line, or look for a stronger moment elsewhere in the transcript.

## What one finished idea actually looks like

The seven parts above, rendered exactly the way they appear in a real menu, one idea in full:

```
**IDEA 1**

**Title:** The "Say It Out Loud" Pricing Script

**Format:** A one-page printable script, three short scenarios

**Core Problem:** People rehearse their pricing structure endlessly but
never rehearse the actual sentence that comes out of their mouth. Two
attendees flat out asked for exact words to say, not another strategy
session.

**Microsolution:** Three ready-to-say scripts for the moment someone asks
"what's the investment," so the reader has words in their mouth before
they need them.

**Why This Converts:** This is the single clearest, most specific ask in
the whole session. Two different attendees said almost the same thing
within a minute of each other.

**Pitch Line:** "You already know your price. This gives you the exact
words to say it without flinching."

**Source:** "Can we just get the actual words? Like a script? Because I
freeze every time I have to say the number." (line 24) · "I think I
freeze. Like I've rehearsed the number in my head but never actually
said it out loud to a real person, so when it's real I panic and
undersell it." (line 20)
```

Bolded title and part-labels, a blank line between parts, the Source line last with its quote(s) and line reference(s) in the exact punctuation shown. See `examples.md` and `sample/expected-output-menu.txt` for a complete three-idea menu with dividers between ideas.
