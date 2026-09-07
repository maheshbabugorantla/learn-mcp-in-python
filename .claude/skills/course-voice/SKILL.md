---
name: course-voice
description: Voice, accuracy, and punctuation rules for every piece of prose under */exercises/ — lesson READMEs, module docstrings, FINISHED.md. Load this BEFORE writing or editing any lesson text, never after a review has already found problems. Use it whenever you touch course material, write a "What's next?" pointer, or review someone else's lesson prose.
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

## Machine-written prose

Agents write lesson prose here too, and everything above was written for
human authorship. These rules cover the ways machine-written prose goes
wrong.

- **No AI vocabulary**: delve, crucial, robust, comprehensive, nuanced,
  pivotal, showcase, tapestry, testament, underscore, vibrant, foster,
  intricate, moreover, furthermore, additionally, garner, interplay.
- **No fancy ways to say "is"**: "serves as", "stands as", "boasts",
  "features". Say "is" or "has".
- **No "not just X, but Y."** State the point directly.
- **No filler**: "in order to" is "to", "due to the fact that" is "because",
  and "it is important to note that" is deletable.
- **No abstract metaphor nouns**: substrate, wedge, vantage, nexus, bedrock,
  scaffolding, paradigm, north star, flywheel. Name the concrete thing.
- **No adverb propping up a weak verb.** "significantly improves" is the
  measured delta; "runs quickly" is "is fast", or the number.
- **Prefer the plain word**: use over utilize, use over leverage, help over
  facilitate, many over numerous.

## Em dashes

Two uses are warranted. Rewrite every other one.

**A term, then its gloss**, in a list item, numbered step, or definition:

- `mime_type` — what you're actually returning.

A colon there reads as "a list follows", and a comma buries the term.

**A diagnosis, then the instruction**, in assertion messages, TODO blocks,
and "Stuck?" lines:

> The server lists no `add` tool — register one with @mcp.tool().

The dash makes the pivot one beat instead of two. This is the course's
central teaching move, and the reason the dash survives here at all.

Rewrite the rest:

- **Joining two independent clauses.** Use a full stop, or a colon when the
  second clause explains the first.
- **A mid-sentence aside.** Use commas, or split the sentence.
- **Two on one line.** If a paragraph reaches for two, neither is earning
  its place.
- **In a heading, a title, or a list label.** Never.

When you edit a lesson file, bring its dashes into line with these rules.
Do not open a file only to change punctuation.

## Mechanics

- Straight apostrophes only. Never a curly one.
- Match the file's course idiom: mcp-auth problem READMEs use `## Your task`
  verbatim; mcp-advanced-features uses `## What you'll see until it's built` /
  `## What you'll see fail`; don't import one course's headings into another.
- Don't restate a course's refrain (mcp-ui's "render this / the mimeType is
  how the client knows"); reinforce it, never repeat it.
- In mcp-advanced-features, topics do NOT accumulate — every topic's server
  resets to the base journal. Cross-topic prose hands off conceptually, never
  "add this to the server you just built."

## Forward pointers

A `## What's next?` section carries its own rules, and they are the ones that
have most often shipped wrong. Read `references/forward-pointers.md` before
writing, editing, or reviewing one.
