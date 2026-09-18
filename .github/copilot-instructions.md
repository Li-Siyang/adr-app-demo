# Repository Copilot Instructions

These instructions apply to all coding, documentation, planning, testing, and
delivery work in this repository.

## Repository standards

Follow the applicable repository standards before making changes:

- [Coding standard](standards/coding-standard.md)
- [Branching standard](standards/branching-standard.md)
- [Documentation standard](standards/documentation-standard.md)
- [Jira standard](standards/jira-standard.md)
- [Traceability standard](standards/traceability-standard.md)
- [Testing standard](standards/testing-standard.md)
- [Story delivery Definition of Done](standards/story-delivery-definition-of-done.md)

## Agent responsibilities

Use the role-specific instructions in `.github/agents/`:

- `requirement-agent.agent.md` owns requirement clarification and definitions.
- `planning-agent.agent.md` owns plans, Epics, Stories, and engineering Tasks.
- `developer-agent.agent.md` owns implementation for one approved Story.
- `test-design-agent.agent.md` owns test design before implementation.
- `validation-agent.agent.md` owns independent implementation validation.
- `jira-agent.agent.md` owns Jira execution tracking and synchronization.

Do not duplicate role-specific workflows in this file.

## General rules

- Follow the existing repository architecture and conventions.
- Prefer simple, explicit, testable solutions.
- Keep changes within the approved scope.
- Do not invent requirements or silently resolve requirement gaps.
- Do not duplicate rules whose source of truth is a referenced standard or
  Agent instruction.
