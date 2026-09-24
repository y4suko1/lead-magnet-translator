# Lead Magnet Translator

Turns a group coaching, masterclass, or webinar transcript into a short menu of lead magnet ideas, three to five of them, each grounded in something actually said in the session. Every idea also has to earn its place by being genuinely fun and engaging, not just accurate, since the person it's ultimately for is a potential lead deciding whether to opt in.

Every idea in the menu traces to something specific in the transcript. If the transcript can't genuinely support an idea, that idea doesn't make the menu, even if it would sound good in the abstract.

## Where this fits in a real process

Turning a session recording into a lead magnet, end to end, usually looks something like this by hand:

1. Review any notes taken during the call.
2. Read the transcript and compare it against those notes, adding more.
3. Anonymise the transcript.
4. Get an AI to review the transcript for lead-magnet-worthy ideas.
5. Reconcile the AI's ideas with what came out of steps 1 to 3.
6. Decide on one idea, weighing value, time to build, how simple the funnel is, and whether the next steps are actually ready to go.
7. Create the lead magnet and its landing page.
8. Create the thank-you and nurture emails.
9. Set up the automation for the funnel.
10. Promote it.

**This tool covers steps 1 to 5, not just step 4.** You still anonymise the transcript yourself (step 3), but you can hand this tool your own call notes alongside it, optional, and it uses them to shape which ideas surface, effectively doing step 5's reconciliation as it generates the menu, not leaving you to do that matching up afterward. **It stops short of step 6.** Picking one idea to actually build means weighing funnel simplicity and whether the next steps are ready, judgement calls that stay yours to make.

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

**Turn a transcript into a menu of lead magnet ideas, every time:**

1. Open the Claude Project.
2. Paste in the transcript text, or upload the file (Word, text file, or a text-based PDF, see above).
3. **Optional:** if you took your own notes during the session, paste those in too. This isn't required, the tool works fine from the transcript alone, but if you have notes, sharing them helps the ideas menu reflect what you actually noticed live.
4. Type: "Give me lead magnet ideas from this." (or "...from this transcript and these notes" if you included notes.)
5. You'll get back two things: the ideas menu itself, ready to read and choose from, and a second file alongside it showing exactly where every idea came from, in the transcript and, if you gave notes, in those too. Read the menu. It's the one to work from. Keep the second file only if you want to double-check it.

## What you get back

**The ideas menu**: three to five lead magnet ideas, each with the same seven parts in this order every time: Title, Format, Core Problem, Microsolution, Why This Converts, Pitch Line, and Source (the exact quote and line the idea is built on, so you can check it without opening the second file). If your own call notes shaped an idea too, you'll see a short line saying so underneath. Every idea has to be both grounded in the transcript and genuinely engaging, correct but flat doesn't meet the bar.

If the transcript is thin and can only genuinely support one or two strong ideas, that's what you'll get. A short, real menu beats a full one padded with a weak idea.

**A separate sources file**, named `sources-[date].txt`. This is what proves the ideas menu isn't just taking the AI's word for it. For every idea, it shows the exact words from the transcript, and from your notes if you gave any, that idea is based on. You never need to open this file to use the menu; it's there for anyone who wants to check.

The full contract this output follows, the exact seven parts per idea, and how the sources file is formatted, is written down in [reference/output-schema.md](reference/output-schema.md), so you can check it against any output without needing to ask.

## How to check an idea yourself

Open the sources file, pick an idea, and find its quoted line. Open the transcript and check the words are really there. That's it, no tool needed.

If you'd rather have something do that checking for you, there's an optional tool for it in [verify/](verify/README.md). You never need it to use the translator normally; it's there only if you want to double-check one yourself, and it doesn't need any coding knowledge to run. It checks that quotes are real, it can't tell you whether an idea is any good, that's a judgement call for you.

## Try it on the example

[sample/transcript.txt](sample/transcript.txt) is a made-up transcript (a fictional business, "Coach A," running a fictional group masterclass, no real person, no real session content). [sample/notes.txt](sample/notes.txt) is a made-up set of call notes for the same session, showing what the optional notes input looks like. [sample/expected-output-menu.txt](sample/expected-output-menu.txt) is the correct ideas menu for the transcript and notes together, and [sample/expected-output-sources.txt](sample/expected-output-sources.txt) is its matching sources file, so you can see exactly what a finished result should look like before trying your own transcript.

## What this is not

Not a replacement for anonymising your own transcript, that stays your decision and your step. It stops at the idea stage, it doesn't draft the actual lead magnet, write the landing page, or build the funnel around it, those stay yours to do once you've picked an idea. It also doesn't make the final call on which idea to build, that's a judgement about funnel simplicity and readiness only you can make.
