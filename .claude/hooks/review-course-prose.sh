#!/usr/bin/env bash
# Review one lesson-prose edit against the course-voice skill.
#
# Wired as a PostToolUse command hook. The `if` rule in settings.json has
# already restricted this to Markdown under an exercises/ directory, so the
# checks here are the ones a permission rule cannot express.
#
# Exit codes are the contract with Claude Code:
#   0  nothing to say (not applicable, or the prose is clean)
#   2  findings on stderr; with asyncRewake this wakes the model
set -uo pipefail

# A review must never trigger a review. The nested run inherits this repo's
# settings, so without the sentinel an edit could recurse.
[ -n "${COURSE_PROSE_REVIEW:-}" ] && exit 0

payload=$(cat)
file=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_response.filePath // empty')
[ -n "$file" ] || exit 0
[ -f "$file" ] || exit 0

# Defence in depth. settings.json gates this with an `if` rule, but a script that
# will review a Makefile when run directly is a footgun, so re-check here.
case "$file" in
  *exercises/*.md|*exercises/*/*.md|*exercises/*/*/*.md) ;;
  *) exit 0 ;;
esac

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
skill="$root/.claude/skills/course-voice/SKILL.md"
refs="$root/.claude/skills/course-voice/references"

# Precondition. Staying silent here would hide the fact that the standard is
# gone, so say so once and review nothing rather than reviewing from memory.
if [ ! -f "$skill" ]; then
  echo "course-voice skill not found at ${skill#"$root"/} — lesson prose was not reviewed." >&2
  exit 2
fi

command -v claude >/dev/null 2>&1 || exit 0

read -r -d '' prompt <<PROMPT
Review one lesson edit against this course's prose standard. Read only; change nothing.

Changed file: $file
The standard: $skill
Forward-pointer rules: $refs/forward-pointers.md

1. Read the standard in full. It changes, so read it rather than working from memory.
2. Read the changed file.
3. Judge its prose against every section of the standard: the tone tests, the
   machine-written-prose rules, the em dash rules, and Mechanics.
4. If the file has a "## What's next?" section, read the forward-pointer rules and
   check the pointer against them. Verifying the promise means opening the lesson
   being pointed at, not trusting the directory name.

Report only violations. For each: the file:line, the rule it breaks, the offending
text, and a concrete replacement. Do not restate rules the prose already follows,
do not praise, and do not suggest changes the standard does not require.

If the prose complies with every rule, reply with exactly: CLEAN
PROMPT

findings=$(COURSE_PROSE_REVIEW=1 claude -p --model sonnet "$prompt" 2>/dev/null) || exit 0

# A model that cannot reach the file, or times out, must not read as approval.
[ -n "$findings" ] || exit 0
printf '%s' "$findings" | grep -qx 'CLEAN' && exit 0

{
  echo "course-voice review of ${file#"$root"/}:"
  printf '%s\n' "$findings"
} >&2
exit 2
