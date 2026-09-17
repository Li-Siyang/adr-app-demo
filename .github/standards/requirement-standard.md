# Requirement Standard

## Requirement quality

Requirement Definitions must be:

- explicit;
- unambiguous;
- testable;
- traceable;
- within a defined scope; and
- consistent with other approved requirements.

## Information classification

Requirement-relevant statements must be classified as one of:

- `Confirmed Requirement`: explicitly approved product behavior.
- `Assumption`: an unconfirmed interpretation used temporarily for analysis.
- `Recommendation`: a suggested improvement or option, not a requirement.
- `Open Question`: unresolved information requiring clarification.

Only `Confirmed Requirement` statements may define approved product behavior.
Assumptions, Recommendations, and Open Questions must not be presented as
approved requirements.

## Acceptance criteria

Acceptance criteria must:

- describe observable outcomes;
- be objectively verifiable;
- be traceable to related requirements; and
- avoid prescribing implementation details unless they are explicit constraints.

## Requirement gaps

When information is missing:

- record the gap explicitly;
- explain its impact;
- state the required clarification; and
- do not silently choose a behavior.

## Requirement Definition completion criteria

A Requirement Definition is ready for Human Review only when:

- the business objective and intended users are explicit;
- in-scope and out-of-scope behavior is defined;
- functional requirements, non-functional requirements, business rules,
  constraints, and edge cases have been evaluated;
- acceptance criteria are observable, testable, and traceable;
- assumptions, recommendations, open questions, and requirement gaps are
  explicitly classified;
- no unconfirmed product behavior is presented as an approved requirement;
- blocking gaps are explicitly identified; and
- the document is stored at the canonical path with valid metadata.

New Requirement Definitions must use `Status: DRAFT`. They become approved only
through explicit Human approval.
