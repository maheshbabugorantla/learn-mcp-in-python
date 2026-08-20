# Review instructions for this repo

This is a teaching repo: four MCP courses, each with `NN.problem.*` stub dirs
(learners complete these; their tests MUST fail until solved) and
`NN.solution.*` reference dirs (tests must pass). The shared test file in each
pair is the spec.

When reviewing PRs, check for:

1. **Solved stubs.** Any change that makes a `*.problem.*` suite pass is a
   defect, not a fix — it publishes the answer inside the exercise. Flag it.
2. **Prose claims vs code.** In exercise READMEs, "the test checks X" must
   match actual assertions, sample outputs must match what the code returns,
   and forward pointers ("Next you will…") must describe what the next
   exercise actually asks for — verify against its README and tests.
3. **Paths.** Commands like `uv run pytest exercises/…` resolve from the
   course directory, not the repo root. Makefile examples must name exercises
   that exist in that same course.
4. **Labels.** Module docstrings say `(problem)` in problem dirs and
   `(solution)` in solution dirs.
5. **Tone.** Course prose is firm about the code, never pointed at the
   reader. Flag: "your server" attached to a shortcoming (prefer "the server"
   or "…hasn't X yet"), scolding intensifiers ("never once", "not a single"),
   shouting caps, and clauses that praise the material without informing
   ("…which is the right order to meet them in").
6. **Mechanics.** Straight apostrophes only; `## What's next?` sections end
   the file and must have a body.
