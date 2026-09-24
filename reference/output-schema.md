# Output Schema

This is the fixed contract every output must follow. Every run produces two things: an ideas menu, and a separate sources file.

## The ideas menu

Between three and five ideas. Fewer is fine if the transcript can't genuinely support more; padding with a weak idea is not.

Each idea has the same six parts, in this order:

1. **Title**: the name of the lead magnet, specific and punchy.
2. **Format**: what it is (checklist, mini-guide, quiz, template, swipe file, short video script, worksheet, etc.).
3. **Core Problem**: the specific struggle the transcript raised, grounded in an actual moment, not a generic problem.
4. **Microsolution**: the one small, complete win the lead magnet delivers.
5. **Why This Converts**: the grounded business reasoning, tied to what actually happened in the session.
6. **Pitch Line**: one sentence with real energy a business owner could use to introduce it.

No markdown symbols visible beyond simple labelling. No em dashes. No citations or source lines mixed in. This is the document a business owner reads to pick an idea.

**Both a fidelity bar and a spark bar apply.** An idea that's grounded but flat (generic title, boring angle) fails the spark bar even though it passes fidelity. An idea that's exciting but not traceable to the transcript fails fidelity even though it might read well. Both are required for every idea in the menu.

## The sources file

Named `sources-[YYYY-MM-DD].txt`, delivered alongside the menu, never merged into it. One or more blocks per idea, one block per distinct claim:

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

Unlike the grounding (which a script can verify), whether an idea is genuinely fun and engaging is a judgement call. The tool makes that call as part of its own self-check (see `rules.md` section 6), and a human reader should make the same call before using an idea: would a business owner actually want to build this, and would a lead actually want to opt in for it. A grounded idea that reads flat isn't a finished output; it's a signal to sharpen the title and pitch line, or look for a stronger moment elsewhere in the transcript.
