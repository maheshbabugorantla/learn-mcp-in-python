# learn-mcp-in-python

Four hands-on MCP courses in Python. `mcp-fundamentals` is the base;
`mcp-auth`, `mcp-ui`, and `mcp-advanced-features` branch off it independently.
Each course is a standalone uv project with its own Makefile and lockfile.

## The shape

Every topic dir (`exercises/NN.topic/`) holds `NN.problem.*` / `NN.solution.*`
pairs. The test file (`test_server.py`, or `test_app.py` in mcp-auth) is
byte-identical across each pair — **the tests are the spec**. The problem dir is
a stub the learner completes; the solution dir is the reference answer.

## The two test loops (do not conflate them)

- **Learner's loop**: `make -C <course> test-exercise E=exercises/<topic>/<dir>`
  against a problem dir. It fails until they solve it. That is the product.
- **Author's/CI loop**: `make -C <course> test` verifies every solution stays
  green; `make -C <course> test-problems` verifies every problem stub still
  fails cleanly (pytest exit 1 — not 0, not a collection error).

Never "fix" a failing problem stub. Failing is its job. A problem suite that
passes means someone committed an answer into the teaching material.

## Invariants

- Solved stubs never reach `main`. Coursework lives on personal branches only.
- Before any push: `make -C <course> test` AND `make -C <course> test-problems`
  both pass. The second doubles as the coursework-leak detector.
- Tests resolve from the **course directory**, not the repo root — there is no
  `exercises/` at the repo root. Prose and Makefile examples must match this.
- Each course's Makefile examples name that course's own first exercise
  (cross-course copy-paste here has shipped real bugs).

## Writing or reviewing course prose

- Writing/editing anything under `*/exercises/` (READMEs, docstrings,
  FINISHED.md): load the `course-voice` skill first.
- Auditing course docs, or before opening a PR that touches `*/exercises/`:
  run the `audit-course-docs` skill (it fans out `exercise-auditor` agents).
- Mechanics that are always true: straight apostrophes only (the repo has zero
  curly ones); mcp-auth problem READMEs use `## Your task` verbatim; each
  course has its own heading idioms — match the file you are in.

## Branches, commits, PRs

- Docs branches cut from `main`, one course per branch/PR — the courses are
  file-disjoint, so PRs stay independently mergeable.
- When extracting a user-authored commit: cherry-pick it intact, then land
  corrections as separate commits on top, so authorship and audit stay
  separately reviewable.
- PR bodies list every correction with the `file:line` of the code that
  contradicts the old text, plus a "checked and left alone" section for
  suspected defects that turned out to be fine.
- Commit hygiene (staging by name, no `git add -A`, Conventional Commits) is
  the `story-commit` skill; it applies here.
