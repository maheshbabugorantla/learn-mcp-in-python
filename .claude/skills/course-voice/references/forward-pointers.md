# Forward pointers (`## What's next?`)

Read this before writing or editing a `## What's next?` section. These rules
have shipped wrong more often than any others in the course.

## Placement and grammar

Straight apostrophe in the heading. Append it as the file's last section,
after the "Stuck?" line and any `FINISHED.md` pointer.

## What each file points at

- Topic README: the next **topic**, and why it follows.
- Problem README: the next **exercise** in the topic. The topic's last
  exercise crosses to the next topic.
- Terminal exercise: that course's `FINISHED.md`. The last topic points at
  the sibling courses, which branch off fundamentals independently and can be
  taken in any order.

## Hard rules

Each one generalizes a defect that shipped.

1. **Verify the promise.** The pointer must name something the next lesson
   actually does. Open its README, its work files, and its tests. A directory
   name is not evidence.

   *Shipped:* "Next you will add arguments" when `add` already had both
   arguments. That lesson was about *describing* them.

2. **No paraphrase of the solution twin.** Solution READMEs often end with
   their own transition, and a learner reads problem, then solution, then the
   next problem. Read the twin's closing line first and take a different
   angle.

3. **No spoilers.** Never pre-answer a judgement the next exercise exists to
   teach.

   *Shipped:* a step-1 README handed over the embed-vs-link decision rule
   that step 2 was built around.

4. **No restating a list ten lines above**, and no re-describing the current
   topic when the convention points forward.

## Checking an existing pointer

Walk the pointers in course order rather than per file. Adjacent-file
problems (two blocks saying the same thing, a pointer promising work the next
lesson does not do) are invisible when each file is read alone.
