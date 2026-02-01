---
name: code-implementation
description: Spec-driven and test-driven workflow for implementing new features or code changes. Use when the user asks to create a feature, add functionality, change behavior, or implement code. Require creating plans/<feature-name>/plan.md and plans/<feature-name>/tasks.json, ask the user to review plan.md before coding, and ensure tasks list tests before implementation.
---

# Code Implementation

## Overview
Implement features using a spec-first workflow that transitions into test-driven development (TDD).

## Workflow

### 1) Determine the feature name
- Choose a short kebab-case feature name for the folder `plans/<feature-name>/`.

### 2) Check for an existing spec
- Search for a relevant spec in `plans/`, `docs/`, or README files.
- If found, summarize the spec and confirm it before writing tests.

### ADK subskill (when using google-adk-python)
Apply these steps in addition to the core workflow:
- Define each ADK agent in its own package folder with an `agent.py` entrypoint.
- Move any runner-specific logic into a dedicated `runner.py` module.
- Treat tools as first-class: document the agent's instruction and tools list (even if empty).
- Treat `agent.py` as the source-of-truth for the agent definition and documentation.
- Create clear agent documentation sourced from `agent.py` inside the agent package at `docs/agent.md`.
- Create a matching `.svg` flow diagram inside the agent package at `docs/workflow.svg` based on `agent.py`.

### 3) If no spec exists, elicit requirements and create one
Ask concise questions to clarify scope:
- What problem is the feature solving?
- Who are the users / primary flows?
- Inputs/outputs and edge cases?
- Non-functional constraints (performance, security, compatibility)?
- Acceptance criteria?

Create a spec sheet under `plans/` before coding:
- Path: `plans/<feature-name>/spec.md`
- Template:
  - **Overview**
  - **Requirements**
  - **Inputs/Outputs**
  - **Constraints**
  - **Acceptance Criteria**
  - **Test Plan**

### 4) Create the implementation plan
Before implementing:
- Create `plans/<feature-name>/plan.md` describing how the spec will be implemented.
- Include key modules/files, data flow, risks, and test strategy.

### 5) Create the tasks list (tests first)
Before implementing:
- Create `plans/<feature-name>/tasks.json` with step-by-step tasks.
- Every task must include `task`, `status`, and `comment`.
- Ensure tests appear before any implementation tasks.
- Update task status and comment as work progresses.
- Break tasks into multiple small, sequential steps; each step should be as granular as practical.

Example `tasks.json`:
```json
{
  "tasks": [
    {
      "task": "tests: <feature slice>",
      "status": "pending",
      "comment": "Define expected behavior with failing tests first."
    },
    {
      "task": "impl: <feature slice>",
      "status": "pending",
      "comment": "Implement the minimum to make tests pass."
    }
  ]
}
```

### 6) Request plan review before coding
- Ask the user to review `plan.md` and confirm before writing tests or code.
- Do not proceed until the user approves the plan.

### 7) TDD execution (tests-first)
- **Write failing tests** for the next deliverable (unit → integration as needed).
- Run tests to confirm failures.
- **Implement the minimum code** to pass.
- Refactor with tests green.
- Repeat in small sequential slices (test → implement → green) until the feature is complete.

### 8) Finalize
- Update spec and plan if behavior changes during implementation.
- Summarize changes and test results for the user.
- After completing major task milestones, create `plans/<feature-name>/progress.md` with:
  - Goal of the work
  - Overall status (e.g., on track / blocked / complete)
  - Timestamp (include local date and time)
  - User observations/notes gathered during the work
