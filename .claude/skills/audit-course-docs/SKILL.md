---
name: audit-course-docs
description: Audit course documentation for accuracy and narrative cohesion, and assemble the PR. Use when asked to audit/review exercise docs, or before opening any PR that touches */exercises/.
---

# Audit course docs

The procedure that repeated shipped-then-corrected defects forced into
existence. The expensive lesson underneath it: **a wrong claim caught before
commit is one edit; after push it is a correction commit plus a PR-body
amendment.** Front-load the checking.

## Procedure

1. **Scope the diff.** Confirm it is docs-only — no behavioral change to any
   `server.py` / `db.py` / test file. (Comment/docstring fixes are fine but get
   their own clearly-labelled commit.) If user-authored commits are being
   extracted from a mixed branch, cherry-pick them intact and land corrections
   as separate commits on top.

2. **Fan out one `exercise-auditor` agent per affected course** (they are
   read-only; run them in parallel). Give each the exact commit/branch to
   audit and the course directory.

3. **Verify before fixing.** Reproduce every reported defect against the code
   yourself before editing. The standing example: "your server says no five
   times" looked like a miscount against eleven scope-checked functions — but
   `SUPPORTED_SCOPES` also has five entries and the sentence is narrative, not
   a count. An illustrative number is not a defect; "fixing" it introduces an
   error. Every finding that fails verification goes in the PR body under
   **"checked and left alone"** — reporting the non-fix is part of the audit.

4. **Sequential read-through, pre-commit.** Walk every forward pointer in
   course order and check each against the next lesson's actual task section
   (`## Your task`, `## What you're building`, …). This is the gate that has
   caught what per-file review misses: adjacent blocks saying the same thing,
   pointers promising work the next lesson doesn't do, problem blocks echoing
   their solution twin.

5. **Gates**, per affected course, before push:

   ```sh
   make -C <course> test            # every solution suite green
   make -C <course> test-problems   # every problem stub still starts red
   ```

   `test-problems` is also the proof no coursework leaked into the stubs.

6. **PR body contract**:
   - Each correction: the exact old text quoted, the `file:line` of the code
     or test that contradicts it, what changed.
   - **Checked and left alone**: every suspected defect that verification
     cleared, with why.
   - **Spec currency**: claims that conflict with the protocol revision rather
     than with this repo's code, kept separate because they usually cannot be
     fixed in the same pass. See
     `references/protocol-currency.md`.
   - Verification transcript (the two gate lines per course).
   - Observations that are not defects (pre-existing inconsistencies worth a
     separate change) go in the body, not the diff.

## Commit shape

One commit for the additive narrative work, then one commit per accuracy
defect, named for the defect — never bundled. Staging by name (`story-commit`
rules apply). This keeps "what was authored" and "what the audit corrected"
separately reviewable.
