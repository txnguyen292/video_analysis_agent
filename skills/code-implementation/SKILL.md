---
name: code-implementation
description: Spec-driven and test-driven workflow for implementing new features or code changes. Use when the user asks to create a feature, add functionality, change behavior, or implement code. If a spec exists, follow it and proceed with TDD. If no spec exists, ask for requirements and create a spec sheet under plans/ before coding.
---

# Code Implementation

## Overview
Implement features using a spec-first workflow that transitions into test-driven development (TDD).

## Workflow

### 1) Check for an existing spec
- Search for a relevant spec in `plans/`, `docs/`, or README files.
- If found, summarize the spec and confirm it before writing tests.

### ADK subskill (when using google-adk-python)
Apply these steps in addition to the core workflow:
- Use Context7 to look up `google-adk-python` docs before writing tests or code.
- Define each ADK agent in its own package folder with an `agent.py` entrypoint.
- Move any runner-specific logic into a dedicated `runner.py` module.
- Treat tools as first-class: document the agent's instruction and tools list (even if empty).
- Treat `agent.py` as the source-of-truth for the agent definition and documentation.
- Create clear agent documentation sourced from `agent.py` inside the agent package at `docs/agent.md`.
- Create a matching `.svg` flow diagram inside the agent package at `docs/workflow.svg` based on `agent.py`.

### 2) If no spec exists, elicit requirements and create one
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

### 3) Write an implementation plan and tasks file before coding
Before implementing:
- Create `plans/<feature-name>/plan.md` describing how the spec will be implemented.
- Create `plans/<feature-name>/tasks.json` with step-by-step tasks, each containing:
  - `task`, `status`, `description`, `priority`, `comments`
- Update `tasks.json` as work progresses (status + comments).
- Make the tasks list explicitly **tests-first** (write failing tests before implementations).
 - Place dataclasses or pydantic models in a dedicated `models.py` module (per feature/package).
 - Use this template structure (tests → implementation pairs):

```json
{
  "tasks": [
    {
      "task": "tests: <feature slice>",
      "status": "pending",
      "description": "Write failing tests for <feature slice>.",
      "priority": "high",
      "comments": [
        "TDD: define expected behavior before implementation."
      ]
    },
    {
      "task": "impl: <feature slice>",
      "status": "pending",
      "description": "Implement <feature slice> to satisfy tests.",
      "priority": "high",
      "comments": [
        "Keep scope minimal; refactor after green."
      ]
    }
  ]
}
```

### 4) TDD execution (tests-first)
- **Write failing tests** for the next deliverable (unit → integration as needed).
- Run tests to confirm failures.
- **Implement the minimum code** to pass.
- Refactor with tests green.

### 5) Finalize
- Update spec if behavior changed during implementation.
- Summarize changes and test results for the user.
- After completing major task milestones, create `plans/<feature-name>/progress.md` with:
  - Goal of the work
  - Overall status (e.g., on track / blocked / complete)
  - Timestamp (include local date and time)
