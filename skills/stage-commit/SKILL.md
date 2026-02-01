---
name: stage-commit
description: Split git changes into small, single-purpose commits and stage/commit them with user confirmation. Use when the user asks to stage and commit changes, break work into meaningful chunks, or wants a commit plan and explicit confirmation before each commit.
---

# Stage Commit

## Goal
Create small, single-purpose commits by grouping changes intentionally and confirming commit intent with the user before committing.

## Workflow

1) Inspect changes
- Run `git status -sb` and `git diff --stat`.
- Identify untracked files, deletions, and renames.
- Note files that should not be committed (build artifacts, caches).

2) Group into single-purpose chunks
- Propose commit groups where each group has one concrete purpose (e.g., tests move, feature change, UI tweak, docs update).
- Keep related test updates with their feature change unless explicitly requested otherwise.
- If a file contains multiple purposes, plan to stage it in parts (`git add -p`).

3) Confirm commit plan before committing
- Present the proposed commit list (short purpose + file list) and ask the user to confirm order and messages.
- Do not stage/commit until the user confirms.

4) Stage and commit iteratively
- Stage only the files/hunks for the first commit.
- If pre-commit hooks modify files, restage and rerun commit.
- Commit with an agreed message, then repeat for the next chunk.

5) Validate and report
- After all commits, show `git status -sb` to confirm clean state.
- Summarize commits created.

## Notes
- Prefer `git add -p` when a file mixes unrelated changes.
- Avoid bundling multiple features or refactors in one commit.
- If unsure about grouping, ask a clarifying question instead of guessing.
