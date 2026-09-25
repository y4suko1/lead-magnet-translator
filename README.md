# Lead Magnet Translator

Turns a group coaching, masterclass, or webinar transcript into a short menu of three to five lead magnet ideas, each grounded in something actually said in the session. Every idea also has to earn its place by being genuinely fun and engaging, not just accurate, since the person it's ultimately for is a potential lead deciding whether to opt in.

Every idea in the menu traces to something specific in the transcript. If the transcript can't genuinely support an idea, that idea doesn't make the menu, even if it would sound good in the abstract.

## Where this fits in a real process

Turning a session into a lead magnet by hand means reviewing notes, reading the transcript, anonymising it, generating ideas, reconciling them with what you noticed live, then picking one to actually build before creating it, its emails, and its funnel.

**This tool covers everything up to and including reconciling your notes with the transcript.** You anonymise the transcript yourself; hand this tool your own call notes alongside it (optional) and it folds them into the ideas menu as it goes, rather than leaving you to match them up afterward. It stops before you pick which idea to build. That's a judgement call about funnel simplicity and readiness, and it stays yours.

## Before you use this

The transcript you give this tool is sent to an AI model (Claude) to generate the output. Only use transcripts you're comfortable sharing with an AI model. This tool doesn't check, store, or remove personal information, beyond flagging anything that looks like a real name or identifiable business detail before it goes ahead (see "What it checks before writing anything" below). Anonymising the transcript first is your decision to make, not something this tool does for you.

## What formats it can read

- A Word document (.docx)
- A plain text file (.txt)
- A PDF made from a Word or Google document, meaning you can select and copy the text in it, not a scan or photo of a page
- Text you paste straight into the chat

If you give it anything else, especially a scanned document, it will say so plainly and ask for one of the formats above, rather than guessing at what the scan might say.

## What it checks before writing anything

A group or webinar transcript often names more than one person, or a business itself. If the transcript still has what looks like a real name or identifying detail in it (rather than a placeholder like "Attendee 1"), it will point that out and ask whether you want to continue, before writing anything. This is a quick check-in, not a scan you have to pass. Say yes and it carries on.

## Quick start

**Set up once, in a Claude Project:**

1. In your Claude Project's settings, connect the `lead-magnet-translator` GitHub repository as a knowledge source.
2. Paste this into the Project's **Set project instructions** field:

   > Before responding to anything in this Project, read `identity.md` and `rules.md` in the connected knowledge and follow them exactly. Use `examples.md` to see what a good ideas menu looks like, and what to avoid. Follow `rules.md` section 1 on file formats, section 2 on checking for real names and business details, and section 3 on optional call notes, before writing anything.
   >
   > Before delivering any menu, if code execution and network access to github.com are available in this session, follow `rules.md` section 7a: clone `github.com/y4suko1/lead-magnet-translator` fresh into this session and verify the companion `sources-[date].txt` file against it with `verify/check.py`. Never reconstruct `check.py` from memory or from project knowledge; if the repository can't be cloned, there is no checker to run this session. If code execution isn't available, or the clone fails, follow section 7a's instructions for what to do next rather than silently skipping or substituting for the check.
   >
   > Before delivering any menu, also follow section 7b of `rules.md`: the independent interpretive recheck. It runs every time, whether or not section 7a's checker ran. `check.py` only confirms a quote is real; it says nothing about whether that quote actually supports the count, attribution, or characterisation the menu gives it, which is what 7b checks. If code execution and the cloned repository are available, run `verify/speaker_check.py` to do the mechanical half of this. Either way, finish the full manual recheck in section 7b before showing the reader anything.

**Turn a transcript into a menu of lead magnet ideas, every time:**

1. Open the Claude Project.
2. Paste in the transcript text, or upload the file (Word, text file, or a text-based PDF, see above).
3. **Optional:** if you took your own notes during the session, paste those in too. This isn't required, the tool works fine from the transcript alone, but if you have notes, sharing them helps the ideas menu reflect what you actually noticed live.
4. Type: "Give me lead magnet ideas from this." (or "...from this transcript and these notes" if you included notes.)
5. You'll get back two things: the ideas menu itself, ready to read and choose from, and a second file alongside it showing exactly where every idea came from, in the transcript and, if you gave notes, in those too. Read the menu. It's the one to work from. Keep the second file only if you want to double-check it.

## What you get back

**The ideas menu**: three to five lead magnet ideas, each with the same seven parts in this order every time: Title, Format, Core Problem, Microsolution, Why This Converts, Pitch Line, and Source (the exact quote and line the idea is built on, so you can check it without opening the second file). If your own call notes shaped an idea too, you'll see a short line saying so underneath. Every idea has to be both grounded in the transcript and genuinely engaging, correct but flat doesn't meet the bar.

If the transcript is thin and can only genuinely support one or two strong ideas, that's what you'll get. A short, real menu beats a full one padded with a weak idea.

**A separate sources file**, named `sources-[date].txt`, proves the menu isn't just taking the AI's word for it: the exact transcript (and notes) words behind every idea, so anyone can check without opening a second file. Full output contract in [reference/output-schema.md](reference/output-schema.md).

## How to check an idea yourself

Open the sources file, find the quoted line, check it's really in the transcript. No tool needed.

**If the sources file's header line already says the checker ran** (section 7a: this needs code execution and network access in the chat session, so it won't happen every time), that's already been done for you this session, real and compute-verified, not assumed.

**To run it yourself afterward, or if the header says it didn't run:** an optional script does this mechanically. If you're in a chat session with code execution available, you can just ask "verify this" or "run the checker" and it'll do it there. Otherwise, run it on your own computer from the command line (`python verify/check.py <sources-file> <transcript-file> [notes-file]`) or by dragging the files onto `verify/check.bat`. Full instructions either way: [verify/README.md](verify/README.md). It confirms quotes are real, not whether an idea is any good.

`check.py` confirms a quote is real. It says nothing about whether that quote actually supports the count, attribution, or characterisation a claim gives it, which is what section 7b's recheck is for. `verify/speaker_check.py` does the mechanical half of that: same commands as above, swapping in `speaker_check.py` for `check.py`. Counts get checked on every transcript it can read; attribution ("the host said X") sometimes can't be, on a transcript where it can't confidently tell host from attendee labels, and it says so rather than guessing. See [verify/README.md](verify/README.md) for what that looks like. The rest of section 7b (does the quote's meaning really back the claim) is a manual read, not something either script can do for you.

## Try it on the example

[sample/](sample/) has a made-up transcript and notes (a fictional "Coach A" masterclass, no real content) plus the expected menu and sources output, so you can see a finished result before trying your own.

## What this is not

Not a replacement for anonymising your own transcript, that stays yours to do. It stops at the idea stage: it doesn't draft the lead magnet, its landing page, or its funnel, and it doesn't pick which idea to build. Those decisions stay yours.
