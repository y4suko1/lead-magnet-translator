# Examples

## Example 1: Good output

Given the transcript in `sample/transcript.txt` (a fictional business, "Coach A," running a fictional group masterclass) and the call notes in `sample/notes.txt` (also fictional, showing what the optional notes input looks like), the correct output is two files: `sample/expected-output-menu.txt` (the ideas a business owner actually reads) and `sample/expected-output-sources.txt` (the companion file proving where everything came from).

Notice what makes the menu good:

- Each title is specific and has a hook: "The 'Say It Out Loud' Pricing Script," not "A Guide to Pricing Confidence."
- Each Core Problem points to a real moment in the room (two attendees independently asking for a script, a specific reframe the host offered), not a generic struggle that could belong to any transcript. Counts are exact: "two attendees," never "several" or "many," because the sources file only backs a countable two.
- Each Pitch Line has energy, written the way an excited business owner would actually talk about the idea, not a dry restatement of the problem.
- Bolded titles and part-labels, a divider between ideas, no em dashes, nothing that reads like a spreadsheet.
- Every idea's Source part carries its headline transcript quote(s), checkable without opening the sources file. Ideas 1 and 3 also carry "Also shaped by your own notes," since a call note genuinely backed each, but the Source part itself still shows only transcript quotes, never a notes quote.

Notice what makes the sources file good:

- Every idea has at least one matching `IDEA`/`CLAIM`/`SOURCE` block, and `CLAIM` stays a short label, not a restatement of the idea's reasoning.
- Every `SOURCE:` quote is copied exactly from the transcript, word for word. Where the call notes also backed a claim, the matching `NOTES:` quote is copied exactly from `sample/notes.txt`, sitting in the same block as the `SOURCE:` line it supports, not a separate one.
- Nothing in the menu exists that isn't backed by a source quote here, and no idea relies on a `NOTES:` line alone.

## Example 2: Bad output (what NOT to do)

Below is a deliberately wrong version, using the same transcript. Each problem is labelled so you can see exactly what went wrong and why.

### Bad ideas menu

```
LEAD MAGNET OPPORTUNITIES - SESSION ANALYSIS

Idea 1
Title: 5 Tips for Pricing Confidence
Format: PDF guide
Core Problem: Many business owners struggle with pricing confidence and
imposter syndrome when discussing their rates with potential clients.
Microsolution: A comprehensive overview of confidence-building
techniques for sales conversations.
Why This Converts: Pricing confidence is a universal struggle for
service-based businesses, so this will appeal to a broad audience.
Pitch Line: Learn how to price with confidence.
[WRONG: the title is generic and could belong to any pricing content
anywhere, not something built from this specific session. The Core
Problem is a broad statement about business owners in general, not
grounded in anything a specific attendee said. "Comprehensive overview"
is vague, not a microsolution. The Why This Converts reasoning is
generic ("universal struggle," "broad audience") instead of pointing
to what actually happened in this transcript. The Pitch Line has no
energy at all, it's flat and forgettable. And this whole idea passes a
literal fidelity check, since pricing confidence genuinely was the
topic, while still completely failing the spark requirement.]

Idea 2
Title: The 10-Week Business Transformation Blueprint
Format: Email course
Core Problem: Attendees are on a ten-week journey toward full business
transformation and need ongoing support throughout the program.
Microsolution: Weekly transformational content delivered over ten
weeks to support the group's growth.
Why This Converts: Long-term nurture sequences build trust over time.
Pitch Line: Join us on this transformational journey.
[WRONG: nothing in the transcript mentions a ten-week program at all,
this is invented outright. This is the one failure mode that
disqualifies an idea completely: content with no basis anywhere in
the source. Also generic coaching language throughout ("journey,"
"transformation") instead of anything specific to this session.]

Idea 3
Title: The Confident Pause Cheat Sheet
Format: Printable card
Core Problem: A wavering voice invites negotiation; a steady pause
after stating a price does more to hold it than any discount could.
Source: (none shown)
[WRONG, two ways at once: no SOURCE line anywhere for this idea in
the sources file, so even though this one happens to be genuinely
grounded in the transcript, a reader has no way to check that
without taking the claim on faith. And the menu itself has no
Source part either, when every idea's seventh part is required,
never optional. Every idea needs both a Source part in the menu and
a traceable block in the sources file, not just the ones that feel
most obviously invented.]

Idea 3b
Title: The Pushback Story Reality Check
Core Problem: Multiple people in the room were assuming clients
were mentally negotiating them down before the conversation even
started.
Source: "Constantly. I assume every client is doing math in their
head about how to talk me down." (line 50)
[WRONG: the sources file backs this claim with exactly one SOURCE
line, one attendee, one quote. "Multiple people" overstates a count
the source doesn't support. The Source part's own quote actually
undercuts the claim sitting right above it, a mismatch a self-check
should catch immediately. Should read "One attendee assumed," not
"multiple people."]

Idea 4
Title: The Accountability Tracker
Format: Printable weekly tracker
Core Problem: The business owner's own notes mentioned wanting a
tracker for client accountability between sessions.
[WRONG: this idea's sources file entry has a NOTES line but no
SOURCE line at all, nothing in the transcript itself grounds it, only
the business owner's own aside in their notes. A note can add weight
to an idea, it can never be the only thing backing one. If the
transcript itself doesn't support an idea, that idea doesn't make the
menu, no matter how good it sounds in the notes.]
```

### What's wrong with it, in one line each

A generic title and problem statement that could apply to any pricing content, not something built from this specific room. A justification section that reasons in the abstract ("universal struggle," "broad audience") instead of pointing to what actually happened. An idea invented outright with no basis anywhere in the transcript (the ten-week program). A grounded idea presented with no Source part in the menu and no matching block in the sources file, so it isn't checkable even though it happens to be true. A claim that overstates its own count ("multiple people" when the source shows one), a menu-level version of the same failure a fabricated quote would be, just quieter. An idea backed only by a note, with no transcript quote anywhere, which doesn't meet the bar even though the note itself is real. A flat pitch line with no energy, failing the spark requirement even where the content is accurate.

### The fix

Every idea's title, problem, and pitch line stay specific to this transcript, built from an actual moment, not a generic pricing struggle any business could have. Every idea has a Source part in the menu with its headline transcript quote(s), plus a matching, exact-quote block in the separate sources file for the full detail, never the reverse (a citation in one place but not the other). Every count, sequence, or degree claimed in the menu matches what the sources actually establish, not a rounder or more impressive-sounding version of it. If the transcript can't genuinely support an idea, that idea doesn't make the menu, no matter how good it would sound in the abstract. And every idea earns its place on all fronts: grounded, checkable, and something a person would actually want to click.
