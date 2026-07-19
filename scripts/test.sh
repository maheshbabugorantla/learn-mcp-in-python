#!/usr/bin/env bash
#
# Run every course's *solution* test suite.
#
# Each course is a separate uv project, and within a course every exercise dir
# has its own server.py / test_server.py / db.py — same module names in every
# dir — so pytest can't collect a whole course at once. We run one solution
# directory at a time, from inside its course, exactly the way you would by hand.
#
# Usage:
#   scripts/test.sh                 # all four courses
#   scripts/test.sh mcp-auth        # just one course
#
# Exits non-zero if any solution suite fails.

set -uo pipefail

cd "$(dirname "$0")/.." || exit 1

ALL_COURSES=(mcp-fundamentals mcp-auth mcp-ui mcp-advanced-features)

if [ "$#" -ge 1 ]; then
	COURSES=("$1")
else
	COURSES=("${ALL_COURSES[@]}")
fi

if ! command -v uv >/dev/null 2>&1; then
	echo "error: 'uv' is not installed. See https://docs.astral.sh/uv/getting-started/installation/" >&2
	exit 1
fi

total=0
passed=0
failures=()

for course in "${COURSES[@]}"; do
	if [ ! -d "$course/exercises" ]; then
		echo "error: no such course '$course'" >&2
		exit 1
	fi
	echo "==> $course"
	while IFS= read -r dir; do
		rel=${dir#"$course"/}
		total=$((total + 1))
		if (cd "$course" && uv run pytest "$rel" -q -p no:cacheprovider >/dev/null 2>&1); then
			passed=$((passed + 1))
			echo "  ok   $rel"
		else
			failures+=("$dir")
			echo "  FAIL $rel"
			# Re-run the failing suite so its output lands in the log.
			(cd "$course" && uv run pytest "$rel" -q -p no:cacheprovider 2>&1 | tail -15 | sed 's/^/       /')
		fi
	done < <(find "$course/exercises" -type d -name '*.solution*' | sort)
done

echo
echo "$passed/$total solution suites passed"
if [ "${#failures[@]}" -gt 0 ]; then
	echo "failed:"
	printf '  %s\n' "${failures[@]}"
	exit 1
fi
