# Double-checking an ideas menu yourself

This is entirely optional. You never need it to get an ideas menu out of the tool. It exists only for anyone who wants to check, without taking the AI's word for it, that every quote in a `sources-[date].txt` file really does appear in the transcript it claims to come from.

You don't need to know how to code to use it.

## What you need

Python installed on your computer (a one-time setup, free, from [python.org](https://python.org); search "how to install Python on Windows" if you've not done it before).

You also need this `verify/` folder from the lead-magnet-translator repository. The easiest way is to download the whole repository as a ZIP (green **Code** button on GitHub, then **Download ZIP**) and unzip it.

## How to run it

1. Open `check.bat` in this folder.
2. **Drag the files onto it at once**: the `sources-[date].txt` file (not the ideas menu itself), and the transcript it was generated from. If the ideas menu used call notes and the sources file has any `NOTES:` lines, drag the notes file too, it's optional. (Select the files in your file explorer, click one, then Ctrl+click the others, then drag them together onto `check.bat`.)
3. If you double-click without dragging anything, it'll ask you to type or paste each file path instead, and let you skip the notes file if you don't have one.
4. It prints `PASS` or `FAIL` for each quoted line it checks. If something fails, it shows you exactly what it searched for, so you can judge for yourself. Any `NOTES:` line checked without a notes file given shows `SKIP` instead, not a failure.
5. Press any key to close the window when you're done.

## What this is, and isn't

This is a way to independently confirm a quote is real, separate from the tool's own built-in self-check (described in `rules.md` and the main [README.md](../README.md)). It's not part of getting a menu from the tool normally; most people will never need to open this folder. It checks the sources file, not the ideas menu itself, because the sources file holds an idea's *full* grounding, every claim and quote, not just the one or two headline quotes the menu's own Source line already shows (see `rules.md` section 4, part 7, and section 6).

**It checks that quotes are real. It doesn't check whether an idea is any good.** Whether an idea is fun and engaging, not just accurate, is a judgement call this script can't make, see `reference/output-schema.md` for what that check looks like instead.

Two ready-made examples are in `test-cases/`: `correct-sources.txt` (should print PASS, or SKIP if you leave out the notes file, for everything) and `broken-sources.txt` (deliberately wrong, with several invented or mismatched claims; should print FAIL on most lines, and show you exactly what a caught mistake looks like). Both check against `../sample/transcript.txt`, and `correct-sources.txt` also has a couple of `NOTES:` lines you can check against `../sample/notes.txt`.

Try it yourself:
```
python check.py test-cases/correct-sources.txt ../sample/transcript.txt ../sample/notes.txt
python check.py test-cases/broken-sources.txt ../sample/transcript.txt
```

## If you're comfortable with a terminal

`check.bat` is just a wrapper. The underlying script is `check.py`, and it runs the same way directly:

```
python check.py <sources-file> <transcript-file> [notes-file]
```

The notes file is optional, and only needed if the sources file has `NOTES:` lines you want checked. Same output either way, same exit code (0 if every line passes, 1 if any fail). Use whichever interface you prefer.

## Checking counts and attribution, not just that quotes are real

`check.py` only proves a quote is real. It says nothing about whether a claim built on that quote got the count right ("two attendees" when only one actually said it) or the attribution right (crediting the host with something an attendee said, or the reverse). That's the mechanical half of what `rules.md` section 7b calls the independent interpretive recheck.

`speaker_check.py` does that mechanical half for you, if you're comfortable with a terminal:

```
python speaker_check.py <sources-file> <transcript-file>
```

It maps every quote to the transcript speaker whose turn it falls in, counts distinct speakers behind each claim, and flags a claim whose stated count or host/attendee attribution doesn't match. It's new, added 2026-09-25.

It recognises four transcript label shapes:
- `SPEAKER: dialogue` on one line, including a Zoom VTT-style `Name (username): dialogue` (the `(username)` is dropped from the label it reports).
- Otter.ai-style: a speaker label and timestamp alone on their own line, no colon (`JM  05:12`), dialogue starting the line after.
- Zoom VTT export: a sequence number and a timestamp range on the lines before a `Name (username):` line (both ignored, not mistaken for dialogue or a label).
- Fathom-style: a timestamp first, then the label, on their own line (`0:04 - DH`), dialogue starting the line after.

**If a transcript uses none of these, it says so plainly and stops rather than guessing at turn boundaries.** Its track record against real transcripts so far: an Otter export exposed a real bug (a label shape it matched wrong, silently misattributing a quote), caught by the required section 7b hand-check, then fixed here; a Fathom export used a shape it had never seen at all, correctly refused rather than guess, and that shape was added afterward. The Zoom VTT shape above was built from a real export's format, but hasn't yet been run against a full real Zoom transcript the same way. Treat all four shapes as supported, not as equally proven: Otter and Fathom have each been checked against real transcript content once; Zoom has only been checked against synthetic fixtures built to match its known format. Run it against a real one when you get the chance, the same way the other two were.

**It cannot check everything section 7b covers.** Whether a quote actually supports the strength or characterization a claim gives it ("the comparison worked," "the room reacted well") is a judgement call about meaning, not a structural fact, and this script doesn't attempt it. A clean run here is not a substitute for the full section 7b recheck, every time, it's a second, independent cross-check on the part that genuinely is mechanical.

Try it against the shipped fixtures:
```
python speaker_check.py test-cases/correct-sources.txt ../sample/transcript.txt
python speaker_check.py test-cases/speaker-mismatch-sources.txt ../sample/transcript.txt
```
The second one has two genuinely real quotes (`check.py` passes both) but a wrong claimed count and a wrong attribution, exactly the class of error `check.py` alone can't see.

It also has its own `--selftest`, same idea as `check.py`'s:
```
python speaker_check.py --selftest
```

## Checking that the checker itself works

You don't have to take this script's own correctness on faith either. Run:

```
python check.py --selftest
```

This runs the checker against its own two shipped fixtures in one go: the known-good sample (`test-cases/correct-sources.txt`, which must pass in full) and the deliberately broken one (`test-cases/broken-sources.txt`, where every single quote is either invented outright or subtly altered from the real transcript line, and every one must fail). It prints a clear PASS or FAIL for each fixture and an overall result, exit code 0 only if both behave exactly as expected.

This proves the checker's basic logic holds, not that it catches every conceivable way a quote could be wrong, only the two shapes of wrong its own fixture demonstrates. See the note in `check.py`'s own docstring ("What --selftest actually proves") for the honest limits of what a pass here means.
