# Jira Issue Content

Use concise execution-focused Jira content. Do not copy full source documents
into Jira.

## Epic

### Summary

`[EPIC-ID] Epic Title`

### Description

- Objective:
- Business value:
- Related Requirement IDs:
- Included Story IDs:
- Dependencies:
- Source Requirement:
- Source Development Plan:
- Source Test Design:

## Story

### Summary

`[STORY-ID] Story Title`

### User Story

Use approved Development Plan wording.

### Description

Provide approved execution context only. Do not introduce implementation or
product decisions.

### Related Requirements

- FR-001
- BR-001

### Related Acceptance Criteria

- AC-001-01
- AC-001-02

### Engineering Tasks

- TASK-001-01
- TASK-001-02

### Test Design

- Test Design ID:
- Source:
- Status: APPROVED

### Test Design Evaluation

Use one:

- `TEST_CASES_DEFINED`
- `NO_EXECUTABLE_TEST_REQUIRED`

For `TEST_CASES_DEFINED`, include relevant Scenario IDs and names. For
`NO_EXECUTABLE_TEST_REQUIRED`, include the approved justification and approved
validation method if any.

### Test Coverage Summary

- Test Scenarios:
- Test Cases:
- Acceptance Criteria Coverage:

The approved Test Design remains authoritative.

### Dependencies

Use approved Development Plan dependencies.

### Priority

Use approved Development Plan priority. Do not create or change priority
independently.

### Definition of Done

Use the approved Development Plan Definition of Done where available. Otherwise
the execution-level default may be:

- Approved Story scope is implemented.
- Developer-owned Unit Tests pass.
- Required independent validation is completed.
- Approved Acceptance Criteria are validated.
- No known blocking defects remain.
- Required documentation is updated.
- Pull Request is created.
- Pull Request is reviewed.
- Required Human approval is obtained before merge.

This is an execution policy, not a new product requirement.

### Source Artifacts

- Requirement:
- Plan:
- Test Design:

## Task or Sub-task

- Stable Task ID:
- Title:
- Parent Story:
- Related Story IDs for independent Tasks:
- Purpose:
- Dependencies:
- Completion criteria:
- Source Development Plan:

Do not introduce implementation scope beyond the approved Plan.
