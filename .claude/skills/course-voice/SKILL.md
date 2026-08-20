---
name: course-voice
description: The voice and accuracy rules for writing or editing any prose under */exercises/ — lesson READMEs, docstrings, FINISHED.md. Load BEFORE writing, not after review finds problems.
---

# Course voice

A teaching artifact leads with patience. The reader is mid-course: their
incomplete state is the curriculum's doing, not their failing. Be firm about
what the code should do; never pointed at where the reader currently stands.

## Firm, not abrasive

**The possessive test.** "your server" + a capability credits the reader
("your server describes what the card *is*"). "your server" + a failing
accuses them ("your server has never once looked at the string"). For
failings, either depersonalise ("the server works out who is asking…") or
apply the "yet" reframe.

**The "yet" reframe.** State the same fact as a step in a sequence, not a
deficiency:

- ✗ "Your server has never once looked at the string it is handed."
- ✓ "Your server hasn't looked at the string it is handed yet."

**Banned moves**, each shipped and then had to be removed:

- Curt negation aimed at the reader: "it describes the authorization server,
  **not you**" → "rather than your own".
- Scolding intensifiers about deliberately incomplete state: "never once",
  "not one of them turns a single request away". The previous exercise TOLD
  the learner to stop there.
- Shouting: `**DON'T**`. The course says "Don't." in plain type.

## No editorial rhetoric

**The delete-the-clause test**: remove the clause — did the reader lose
information? If not, the clause was approving of the material instead of
saying something. Cut it.

Real removals: "…rather than re-teaching the protocol primitives",
"the paperwork starts earning its keep", "which is the right order to meet
them in", "That is the spine you just used, doing its job."

Firm factual contrasts are NOT rhetoric — keep them: "reaches the caller as a
500 rather than a 401", "something to check for rather than something to
read".

## Analogies must be earned

An analogy goes in only when it is accurate for *that specific lesson* and a
genuine confusion for its audience. Fundamentals earned REST/GraphQL framing
because tools-vs-endpoints is a real confusion there; the other three courses
got none, because none was true enough. Never port a parallel across lessons,
and never stretch to prove one — no parallel beats a forced parallel.

## Forward pointers (`## What's next?`)

Grammar: straight apostrophe, appended as the file's last section (after the
"Stuck?" line and any FINISHED.md pointer).

- Topic README → the next **topic** and why it follows.
- Problem README → the next **exercise** in the topic; the topic's last
  exercise crosses to the next topic.
- Terminal exercise → that course's `FINISHED.md`. Last topic → the sibling
  courses (they branch off fundamentals independently, any order).

Hard rules, each learned from a shipped defect:

1. **Verify the promise.** The pointer must name something the next lesson
   actually does — check its README, work files, and tests, never the
   directory name. ("Next you will add arguments" shipped when `add` already
   had both arguments; the next lesson was about *describing* them.)
2. **No paraphrase of the solution twin.** Solution READMEs often end with
   their own transition. A learner reads problem → solution → next problem;
   read the twin's closing line first and take a different angle.
3. **No spoilers.** Never pre-answer a judgement the next exercise exists to
   teach. (Step 1's README once handed over the embed-vs-link decision rule
   that step 2 was built around.)
4. **No restating a list ten lines above**, and no re-describing the current
   topic when the convention points forward.

## Mechanics

- Straight apostrophes only — the repo has zero curly ones.
- Match the file's course idiom: mcp-auth problem READMEs use `## Your task`
  verbatim; mcp-advanced-features uses `## What you'll see until it's built` /
  `## What you'll see fail`; don't import one course's headings into another.
- Don't restate a course's refrain (mcp-ui's "render this / the mimeType is
  how the client knows" already appears 4×; reinforce, never repeat).
- In mcp-advanced-features, topics do NOT accumulate — every topic's server
  resets to the base journal. Cross-topic prose hands off conceptually, never
  "add this to the server you just built."
