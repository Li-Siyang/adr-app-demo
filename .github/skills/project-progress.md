# Project Progress Summary

Use this skill when the user asks to summarize the current project progress,
development status, implementation status, or similar repository state.

## Scope

Summarize the current repository only. Do not inspect Copilot session history,
other worktrees, or unrelated repositories.

Do not modify files, create commits, run destructive commands, or change issue
and pull request data.

## Evidence to inspect

Inspect the following sources when available:

1. Current Git branch and working-tree status.
2. Recent commit history.
3. The diff from the working tree and the current branch's recent commits.
4. Repository TODO, FIXME, and unfinished-work markers.
5. Relevant project documentation, issue references, and pull request
   references already present in the repository.
6. The project's existing test, build, and lint configuration and the latest
   available evidence from those checks. Do not run expensive or
   potentially-destructive commands solely for this summary.
7. The canonical planning and delivery artifacts needed to count User Stories
   and determine their completion status.

Prefer direct repository evidence over assumptions. If a check has not been
run or its result is unavailable, say so explicitly.

## Story progress

Report the total number of distinct User Stories and their progress using
separate delivery and validation counts.

Use the canonical planning artifact, normally
`docs/planning/PLAN-*.md`, to identify the complete set of User Story IDs.
Count each Story ID once, even when it appears in multiple traceability,
dependency, task, or test sections. Do not count Engineering Tasks, Epics,
Requirements, test cases, or incidental references as Stories.

Determine **delivered** status from explicit repository evidence such as a
merged Story feature branch or pull request, a completed delivery artifact,
or a commit series clearly implementing the Story with its own tests. Do not
infer delivery solely because a Story appears in a plan, has unrelated
implementation files, or is referenced by a passing test for another Story.

Determine **independently validated** status only from an explicit validation
or test-result artifact for that Story marked passed, or equivalent direct
evidence. A Story can therefore be delivered but not independently validated.
Do not claim that a delivered Story satisfies the full Definition of Done
when the repository lacks its required validation, traceability, review, or
handoff evidence.

## Response format

Return a concise Markdown report with these headings:

## Story progress

Report:

- `delivered / total` User Stories, listing the delivered Story IDs and their
  implementation, commit, pull request, or test evidence.
- `independently validated / total` User Stories, listing the validated Story
  IDs and their validation evidence.
- Any delivered Stories that are not yet independently validated or do not
  have enough evidence for the full Definition of Done.

If a count cannot be established reliably, report it as unknown rather than
guessing.

## Completed

List functionality or work supported by commits, files, or other direct
evidence. If there is no verified completed work, say so.

## In progress

Describe uncommitted changes, the active branch, and work that appears to be
underway. Distinguish staged, unstaged, and untracked changes when relevant.

## Unfinished

List TODOs, FIXMEs, missing implementation, unresolved documentation, and
other work that is directly visible in the repository.

## Verification

Report the latest known test, build, and lint results. Include the command and
result when available. Never imply that an unrun check passed.

## Risks and next steps

Report concrete blockers, stale or conflicting evidence, and the smallest
reasonable next steps. Do not invent priorities or requirements.

Keep the report factual and concise. Clearly label unknown information as
unknown rather than filling gaps with guesses.
