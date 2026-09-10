# Test Design: Internal Decision Record MVP

**Test Design ID:** TEST-001  
**Status:** Approved  
**Mode:** DESIGN MODE  
**Source Requirement:** `docs/requirements/requirement-definition.md`, Version 1.1, Approved
**Source Development Plan:** `docs/planning/PLAN-001-internal-decision-record-mvp.md`, explicitly provided as approved  
**Scope:** STORY-001 through STORY-016  

## Readiness Assessment

- The Requirement Definition is explicitly Approved.
- The Development Plan was explicitly provided as approved and reports no blocking
  or non-blocking requirement gaps.
- Every planned Story identifies related Requirements and source Acceptance
  Criteria.
- The approved Acceptance Criteria are observable and testable.
- No unresolved product question blocks this design.
- Expected behavior in this design comes only from the approved Requirement
  Definition and Development Plan. Jira and production implementation were not
  used.

## Test Scenarios

| Scenario ID | Title | Related Story | Related Requirements | Related AC | Objective | Test Type | Priority |
|---|---|---|---|---|---|---|---|
| TS-001 | Enforce organizational authentication and team access | STORY-001 | CR-USR-001–002; CR-FR-001–002; CR-NFR-001–002 | AC-001 | Verify SSO access is limited to authenticated designated-team members and removed when membership is lost. | Acceptance / Integration / Security / Negative | High |
| TS-002 | Enforce additive governed roles | STORY-002 | CR-USR-004–006, CR-USR-009–010; CR-FR-009–010; CR-BR-001–002, CR-BR-013, CR-BR-015 | AC-003, AC-006–007, AC-023 | Verify administrator-only operations, approver authority, self-approval, and additive permissions. | Acceptance / Authorization / Business Rule | High |
| TS-003 | Create a complete structured Draft | STORY-003 | CR-BG-001–002; CR-OBJ-001–002; CR-USR-003, CR-USR-007; CR-FR-003–005, CR-FR-006A, CR-FR-023; CR-BR-010 | AC-002, AC-004, AC-037 | Verify Draft creation captures required context, separate author and owner, tags, and the prohibited-information notice. | Acceptance / E2E / Business Rule | High |
| TS-004 | Edit and submit a Draft | STORY-004 | CR-USR-003; CR-FR-006–008, CR-FR-024; CR-BR-003, CR-BR-016 | AC-004–005, AC-024 | Verify author editing and guarded Draft-to-Proposed submission. | Acceptance / Negative / Boundary / State Transition | High |
| TS-005 | Decide and restart review of a proposal | STORY-005 | CR-FR-006–010, CR-FR-014; CR-BR-002–004 | AC-006–008, AC-038 | Verify authorized outcomes, self-decision, review invalidation after edits, and terminal immutability. | Acceptance / Business Rule / State Transition / Concurrency | High |
| TS-006 | Transfer ownership without changing authorship | STORY-006 | CR-USR-007–008; CR-FR-006A, CR-FR-026; CR-BR-011 | AC-014, AC-030 | Verify the actor/state authorization matrix and handling after author departure. | Acceptance / Authorization / State Transition | High |
| TS-007 | Create and resolve one replacement version | STORY-007 | CR-USR-009; CR-FR-011–013; CR-BR-005–006, CR-BR-013–014 | AC-009–011, AC-025, AC-039 | Verify controlled replacement creation, the active-replacement limit, and atomic supersession. | Acceptance / Integration / Business Rule / State Transition | High |
| TS-008 | Preserve immutable history and version navigation | STORY-008 | CR-OBJ-002; CR-FR-013–014; CR-NFR-003; CR-BR-004–006, CR-BR-009 | AC-012–013, AC-038 | Verify bidirectional version navigation, complete change attribution, and immutable historical content. | Acceptance / Integration / Security | High |
| TS-009 | Discover authorized records by one exact tag | STORY-009 | CR-FR-005, CR-FR-015–016; CR-BR-009 | AC-015 | Verify exact matching includes current, rejected, superseded, and archived records. | Acceptance / Integration / Negative | High |
| TS-010 | Create and govern tags without record loss | STORY-010 | CR-FR-025; CR-BR-017 | AC-029, AC-040–042 | Verify team creation, administrator maintenance, reference propagation, and record preservation. | Acceptance / Integration / Authorization / Business Rule | High |
| TS-011 | Discuss records with single-level auditable comments | STORY-011 | CR-USR-002; CR-FR-017–019; CR-BR-012 | AC-016–019, AC-028 | Verify comments, one reply level, author-only soft deletion, reply preservation, and audit evidence. | Acceptance / Integration / Negative / Concurrency | High |
| TS-012 | Archive and restore lifecycle records | STORY-012 | CR-USR-006; CR-FR-020–021; CR-BR-007, CR-BR-014; CR-NFR-008 | AC-003, AC-020–021, AC-026, AC-034 | Verify administrator-only archival, discovery and retention, exact restoration, and the replacement guard. | Acceptance / Integration / State Transition / Business Rule | High |
| TS-013 | Permanently delete only eligible Drafts | STORY-013 | CR-FR-022; CR-BR-008; CR-NFR-007–008 | AC-022, AC-027, AC-033–034 | Verify the actor/state deletion matrix, complete ordinary-data removal, non-restorability, and permanent minimal audit evidence. | Acceptance / Integration / Security / Negative | High |
| TS-014 | Protect confidential application data | STORY-014 | CR-SCP-003; CR-NFR-001–002, CR-NFR-005 | AC-001, AC-032 | Verify the team boundary and encryption of all in-scope data in transit and at rest. | Security / Integration / Configuration | High |
| TS-015 | Audit and permanently retain governed events | STORY-015 | CR-FR-014, CR-FR-019–022; CR-NFR-007–008 | AC-013, AC-018, AC-027, AC-033–034 | Verify every approved event category is audited, immutable, and has no expiry or permanent deletion path. | Integration / Audit / Retention | High |
| TS-016 | Meet approved capacity and response targets | STORY-016 | CR-SCP-002; CR-NFR-004, CR-NFR-006 | AC-031 | Verify functionality and two-second primary-content usability at 25-user/1,000-record capacity. | Non-functional / Performance / E2E | High |
| TS-017 | Meet backup and recovery targets | STORY-016 | CR-NFR-009 | AC-035 | Verify daily backup, RPO no greater than 24 hours, and RTO no greater than 8 hours. | Non-functional / Recovery / Operational | High |
| TS-018 | Support approved browser versions | STORY-016 | CR-NFR-011 | AC-036 | Verify all in-scope functions in current and prior major Chrome and Edge versions. | Compatibility / E2E | High |

## Test Cases

### STORY-001 — Authenticate and Restrict Team Access

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|
| TC-001-01 | TS-001 | CR-FR-001–002; CR-NFR-001–002 | AC-001 | User is an authenticated member of the designated team. | Complete organizational SSO; open the application and a decision record. | The member can access the application and authorized decision records. | High | E2E |
| TC-001-02 | TS-001 | CR-FR-001–002; CR-NFR-001–002 | AC-001 | User is unauthenticated. | Attempt to open the application and a direct decision-record reference. | Both access attempts are denied and no decision data is exposed. | High | E2E |
| TC-001-03 | TS-001 | CR-FR-002; CR-NFR-001–002 | AC-001 | User is authenticated but is not a designated-team member. | Attempt to open the application and a direct decision-record reference. | Both access attempts are denied and no decision data is exposed. | High | Integration |
| TC-001-04 | TS-001 | CR-FR-002; CR-NFR-001–002 | AC-001 | An authenticated member has an active session, then loses team membership. | Remove team membership; attempt further application and record access. | The user is no longer granted application or decision-record access. | High | Integration |

### STORY-002 — Administer Additive Roles and Approvers

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|
| TC-002-01 | TS-002 | CR-USR-004, CR-FR-009; CR-BR-001 | AC-003 | Administrator and ordinary member exist. | As administrator designate an approver; as ordinary member attempt the same. | Administrator succeeds; ordinary member is denied. | High | Acceptance |
| TC-002-02 | TS-002 | CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | Non-administrator has application access; eligible records exist. | Attempt archive, restore, and Accepted-record replacement creation. | Every administrator-only action is denied. | High | API |
| TC-002-03 | TS-002 | CR-FR-009 | AC-006 | Proposed record exists; actor is not a designated approver. | Attempt both Accept and Reject. | Both decisions are denied and the proposal has no new outcome. | High | API |
| TC-002-04 | TS-002 | CR-USR-005; CR-FR-010; CR-BR-002 | AC-007 | Proposed record author is also a designated approver. | Decide the authored proposal once as Accept and, on an equivalent proposal, once as Reject. | Each selected transition succeeds. | High | Acceptance |
| TC-002-05 | TS-002 | CR-USR-010; CR-BR-015 | AC-023 | One user holds multiple approved roles with distinct permissions. | Attempt one action granted by each held role. | Every action granted by any held role is permitted; no held role removes another role's permission. | High | API |

### STORY-003 — Create a Complete Draft

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-003-01 | TS-003 | CR-FR-003–005, CR-FR-006A | AC-002 | Authenticated team member; an owner and one or more tags are available. | Create a record with title, context, decision, rationale, alternatives, consequences, owner, decision date, and tags. | A Draft is created; creator is author; owner is stored separately; all required content and at least one tag are retained. | High | E2E |
| TC-003-02 | TS-003 | CR-FR-004 | AC-004 | Draft creation is available. | For each required field in turn, leave that field empty while supplying the others; attempt submission. | Submission is prevented and the omitted required field is identified in every iteration. | High | Acceptance |
| TC-003-03 | TS-003 | CR-FR-023; CR-BR-010 | AC-037 | Authenticated team member. | Open the record creation screen and an existing editable record's edit screen. | Both screens visibly state that regulated personal information and health information must not be entered. | High | E2E |

### STORY-004 — Edit and Submit a Draft

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|
| TC-004-01 | TS-004 | CR-USR-003; CR-FR-006 | — | Author owns an authored Draft. | Change editable content and save. | The changed Draft content is retained. | High | Acceptance |
| TC-004-02 | TS-004 | CR-USR-003; CR-FR-006 | — | A Draft exists; actor is not its author. | Attempt to edit and save record content. | The edit is denied and content is unchanged. | High | API |
| TC-004-03 | TS-004 | CR-FR-007–008 | AC-005 | Authored Draft has every required field and at least one designated approver. | Submit the Draft. | Status changes from Draft to Proposed. | High | E2E |
| TC-004-04 | TS-004 | CR-FR-004, CR-FR-024; CR-BR-016 | AC-004, AC-024 | Authored Draft is incomplete and has no designated approver. | Attempt submission. | It remains Draft; every missing required field is identified; an actionable message states that at least one designated approver is required. | High | Acceptance |
| TC-004-05 | TS-004 | CR-FR-024; CR-BR-016 | AC-024 | Authored Draft is complete but has zero designated approvers. | Attempt submission. | It remains Draft and the actionable approver-required message is shown. | High | Acceptance |

### STORY-005 — Review and Decide a Proposal

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|
| TC-005-01 | TS-005 | CR-FR-008–010 | AC-006–007 | Equivalent Proposed records exist for a designated approver and non-approver. | Have each actor attempt Accept and Reject. | Designated approver transitions each proposal to the selected outcome; non-approver is denied. | High | API |
| TC-005-02 | TS-005 | CR-FR-006, CR-FR-008; CR-BR-003 | AC-008 | Authored Proposed record has prior or in-progress review. | Author edits and saves the proposal; attempt a decision before resubmission; then resubmit. | Save returns it to Draft, invalidates all review, and prevents a decision until it is resubmitted to Proposed. | High | Integration |
| TC-005-03 | TS-005 | CR-FR-014; CR-BR-004 | AC-038 | Rejected record exists. | As each relevant role attempt content, lifecycle-data, and version-content changes; archive and restore separately as administrator. | All record changes are denied; only the separate archival condition may change. | High | API |
| TC-005-04 | TS-005 | CR-FR-008 | — | One Proposed record is available to two designated approvers concurrently. | Initiate conflicting Accept and Reject decisions. | Exactly one lifecycle outcome is committed; the record cannot become both Accepted and Rejected. | High | Integration |

### STORY-006 — Transfer Record Ownership

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|
| TC-006-01 | TS-006 | CR-USR-007–008; CR-FR-006A; CR-BR-011 | AC-014 | Draft and Proposed records exist. | For each state, transfer ownership as author, current owner, and administrator. | Every transfer succeeds; owner changes and author remains unchanged. | High | API |
| TC-006-02 | TS-006 | CR-FR-006A; CR-BR-011 | AC-014 | Draft/Proposed records and Accepted/Rejected/Superseded records exist. | Attempt transfer as an unrelated user on editable states and as any user on non-editable states. | Every unauthorized actor/state combination is denied; owner and author remain unchanged. | High | API |
| TC-006-03 | TS-006 | CR-FR-026 | AC-030 | A record's author has left the team; owner and administrator remain. | Confirm record retention; attempt actions otherwise granted to owner/admin; attempt author-only editing without another grant. | Record remains; owner/admin retain only otherwise-granted actions; departure grants no extra editing permission. | High | Integration |

### STORY-007 — Create and Decide a Replacement Version

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-007-01 | TS-007 | CR-FR-011; CR-BR-004–005 | AC-009 | Accepted record exists. | As multiple roles attempt direct record editing. | Direct editing is prevented and Accepted content is unchanged. | High | API |
| TC-007-02 | TS-007 | CR-FR-012; CR-BR-005, CR-BR-013–014 | AC-010 | Accepted record has no active replacement. | Administrator starts a replacement. | A linked Draft is created, original Accepted record is unchanged, and the Draft counts as active immediately. | High | Integration |
| TC-007-03 | TS-007 | CR-FR-012; CR-BR-013 | AC-003 | Accepted record has no active replacement; actor is not administrator. | Attempt replacement creation. | Creation is denied and no replacement exists. | High | API |
| TC-007-04 | TS-007 | CR-FR-012; CR-BR-014 | AC-025 | Accepted record has an active Draft or Proposed replacement. | Administrator attempts a second replacement. | Creation is denied and exactly one active replacement remains. | High | Integration |
| TC-007-05 | TS-007 | CR-FR-013; CR-BR-006 | AC-011, AC-039 | A replacement is Proposed and its original is Accepted. | Accept the replacement. | Replacement becomes Accepted, original atomically becomes Superseded, links remain, and no active replacement remains. | High | Integration |
| TC-007-06 | TS-007 | CR-FR-012; CR-BR-014 | AC-039 | Separate active replacements exist in equivalent fixtures. | Reject one and delete another while Draft. | Each ceases to count as active; its original remains Accepted; a new replacement may subsequently be started. | High | Integration |

### STORY-008 — View Immutable Change and Version History

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-008-01 | TS-008 | CR-FR-013 | AC-012 | Linked Superseded original and Accepted replacement exist. | View each version and navigate to the related version. | Navigation succeeds in both directions and resolves to the correct linked record. | High | E2E |
| TC-008-02 | TS-008 | CR-FR-014; CR-NFR-003 | AC-013 | Record has known changes by known actors at known times. | View history and compare each entry to the changes; attempt to modify entries. | History identifies what, who, and when for each change; entries cannot be modified. | High | Integration |
| TC-008-03 | TS-008 | CR-FR-014; CR-NFR-003; CR-BR-004, CR-BR-009 | AC-038 | Rejected and Superseded records exist. | Attempt content, lifecycle-data, and version-content changes; then retrieve both records. | Changes are denied; both records and their histories remain available to authorized users. | High | Integration |
| TC-008-04 | TS-008 | CR-FR-013–014 | AC-012–013 | A multi-version chain exists. | Traverse all related links and inspect history. | Links resolve to the intended versions without cycles or history corruption. | High | Integration |

### STORY-009 — Discover Records by Exact Tag

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-009-01 | TS-009 | CR-FR-015–016; CR-BR-009 | AC-015 | Authorized user; exact target tag is assigned to Draft, Proposed, Accepted, Rejected, Superseded, and archived records. | Apply the target tag as the single exact filter. | Every authorized record with that exact tag is returned, including Rejected, Superseded, and archived records. | High | E2E |
| TC-009-02 | TS-009 | CR-FR-015 | AC-015 | Records have the target tag, a longer tag containing the target text, and an unrelated tag. | Apply the target exact tag filter. | Only records assigned the exact selected tag are returned. | High | Integration |
| TC-009-03 | TS-009 | CR-FR-016; CR-NFR-001–002 | AC-001, AC-015 | Matching records include data the actor is not authorized to access. | Apply the exact tag filter. | Only authorized matching records are exposed. | High | Integration |

### STORY-010 — Create and Govern Tags

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-010-01 | TS-010 | CR-FR-025 | AC-029 | Authenticated team member. | Create a tag and assign it to a record. | The tag is available for assignment and is retained on the record. | High | Acceptance |
| TC-010-02 | TS-010 | CR-FR-025 | AC-029 | Non-administrator; existing tags. | Attempt rename, merge, and deletion. | All three maintenance actions are denied and references are unchanged. | High | API |
| TC-010-03 | TS-010 | CR-FR-025; CR-BR-017 | AC-040 | Administrator; one tag is associated with multiple records. | Rename the tag. | Every associated record references the renamed tag; no associated record is deleted. | High | Integration |
| TC-010-04 | TS-010 | CR-FR-025; CR-BR-017 | AC-041 | Administrator; source tag is associated with multiple records; target tag exists. | Merge source into target. | Target replaces source on every source-associated record; no associated record is deleted. | High | Integration |
| TC-010-05 | TS-010 | CR-FR-025; CR-BR-017 | AC-042 | Administrator; tag is associated with multiple records. | Delete the tag. | Only that tag association is removed from every associated record; all records and other tags remain. | High | Integration |

### STORY-011 — Discuss a Decision

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-011-01 | TS-011 | CR-USR-002; CR-FR-017 | AC-016 | Authenticated team member views a record. | Add a top-level comment. | The comment is visible on that record. | High | E2E |
| TC-011-02 | TS-011 | CR-FR-018 | AC-017 | Top-level comment exists. | Another authenticated member adds a reply. | One reply level is visible with the top-level comment. | High | Acceptance |
| TC-011-03 | TS-011 | CR-FR-019; CR-BR-012 | AC-018 | Comment author has a comment with replies. | Author deletes the comment. | `[deleted]` replaces content, replies remain visible, and deletion audit evidence is retained. | High | Integration |
| TC-011-04 | TS-011 | CR-FR-019; CR-BR-012 | AC-019 | Another user's comment exists. | Attempt to delete it. | Deletion is denied; comment and replies are unchanged. | High | API |
| TC-011-05 | TS-011 | CR-FR-018 | AC-028 | A reply exists. | Attempt to reply to that reply. | Nested-reply action is unavailable or denied; no nested reply is created. | High | Acceptance |
| TC-011-06 | TS-011 | CR-FR-018–019; CR-BR-012 | AC-017–018 | A top-level comment exists. | Concurrently request a reply and author deletion. | Final state has the `[deleted]` placeholder, the reply, and a deletion audit entry. | High | Integration |

### STORY-012 — Archive and Restore Records

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-012-01 | TS-012 | CR-FR-020; CR-BR-007; CR-NFR-008 | AC-020, AC-034 | Administrator; records exist in each lifecycle status with no replacement guard. | Archive each record and discover it as an authorized user. | Each is marked archived, retained without expiry, and remains discoverable. | High | Integration |
| TC-012-02 | TS-012 | CR-USR-006; CR-FR-020–021; CR-BR-007 | AC-003 | Non-administrator; active and archived records exist. | Attempt archive and restore. | Both actions are denied and archival conditions are unchanged. | High | API |
| TC-012-03 | TS-012 | CR-FR-021 | AC-021 | Administrator; separately archived records previously held each lifecycle status. | Restore each record. | Each returns to exactly the lifecycle status held immediately before archival. | High | Integration |
| TC-012-04 | TS-012 | CR-FR-020; CR-BR-014 | AC-026 | Original Accepted record has an active Proposed replacement. | Attempt to archive original; reject the replacement and retry on equivalent data; accept it and evaluate the former original. | Archive is denied while replacement is Proposed; the active-Proposed block no longer applies after Accepted or Rejected resolution. | High | Integration |
| TC-012-05 | TS-012 | CR-FR-021–022 | AC-021, AC-027 | A Draft is archived and then restored by an administrator. | After restoration, have an authorized actor permanently delete it. | Restoration returns it to Draft and the Draft deletion rules apply. | High | Integration |

### STORY-013 — Permanently Delete an Eligible Draft

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-013-01 | TS-013 | CR-FR-022; CR-BR-008 | AC-027 | Equivalent current Drafts contain content, comments, and ordinary history. | Delete one as author, one as owner, and one as administrator. | Each deletion succeeds; content, comments, and ordinary history are unavailable and non-restorable; permanent minimal audit event contains record ID, actor, and timestamp. | High | Integration |
| TC-013-02 | TS-013 | CR-FR-022; CR-BR-008 | AC-027 | Current Draft exists; actor is neither author, owner, nor administrator. | Attempt permanent deletion. | Deletion is denied and all Draft data remains. | High | API |
| TC-013-03 | TS-013 | CR-FR-022; CR-BR-008 | AC-022 | Proposed, Accepted, Rejected, and Superseded records exist. | Attempt permanent deletion of each as every otherwise relevant actor. | Action is unavailable or denied for every non-Draft; records remain archive-only. | High | API |
| TC-013-04 | TS-013 | CR-NFR-007–008 | AC-033–034 | A Draft has been permanently deleted. | Inspect retained event and available retention/deletion actions. | Event has record ID, actor, timestamp, no expiry, and no permanent-deletion action; removed ordinary data remains unavailable. | High | Integration |

### STORY-014 — Protect Confidential Application Data

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-014-01 | TS-014 | CR-NFR-001–002 | AC-001 | Representative confidential decision records exist. | Repeat unauthenticated, non-team, and removed-member access attempts across application and direct record entry points. | Unauthorized users receive no access or confidential record data. | High | Security / Integration |
| TC-014-02 | TS-014 | CR-NFR-005 | AC-032 | In-scope data flows and storage locations are available for inspection. | Inspect transmission of application data and every in-scope persisted data category. | Application data is encrypted in transit and at rest. | High | Security / Integration |

### STORY-015 — Audit and Permanently Retain Governed Events

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-015-01 | TS-015 | CR-NFR-007 | AC-033 | Actors and records support all governed event categories. | Trigger authentication, role change, approver designation change, lifecycle transition, archive, restore, ownership transfer, comment deletion, and permanent Draft deletion. | A corresponding audit record is created for every event category. | High | Integration |
| TC-015-02 | TS-015 | CR-NFR-007; CR-FR-022 | AC-027, AC-033 | Eligible Draft exists. | Permanently delete it and inspect the surviving audit event. | Surviving minimal event contains record ID, actor, and timestamp. | High | Integration |
| TC-015-03 | TS-015 | CR-FR-014; CR-NFR-007–008 | AC-013, AC-034 | Audit entries and archived records exist. | Attempt modification, expiry assignment, and permanent deletion through available interfaces; inspect retention controls. | Audit entries cannot be modified; no retention expiry or permanent deletion action applies to audit entries or archived records. | High | Security / Integration |

### STORY-016 — Meet Capacity and Operational Targets

| Test Case ID | Parent Scenario | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-016-01 | TS-016 | CR-SCP-002; CR-NFR-004 | AC-031 | 1,000 decision records and test activity within the 25-user capacity. | Exercise all in-scope functional workflows with activity up to the approved capacity. | The MVP remains functional for up to 25 authorized users and 1,000 records. | High | Integration / E2E |
| TC-016-02 | TS-016 | CR-NFR-006 | AC-031 | Approved-capacity dataset and user activity; observable user-action and primary-content-usable timestamps. | Open record list, open record detail, and apply an exact single-tag filter; measure each complete interaction. | Primary content for each interaction is usable within two seconds from the initiating user action. | High | E2E |
| TC-017-01 | TS-017 | CR-NFR-009 | AC-035 | Operational backup environment and recoverable representative data exist. | Observe scheduled backups across each daily interval; restore from an eligible recovery point and measure data loss and elapsed recovery time. | Backup occurs daily; restored data loses no more than 24 hours; restoration completes within 8 hours. | High | Integration / Manual |
| TC-018-01 | TS-018 | CR-NFR-011 | AC-036 | Current and immediately prior major Chrome and Edge versions are identified at execution time. | Execute all in-scope acceptance workflows on each of the four browser/version combinations. | Every in-scope function is supported in each approved browser/version combination. | High | E2E |

## Cross-Story Regression Risks

| Risk | Stories Most Exposed | Required Regression Focus |
|---|---|---|
| Authorization changes expose confidential data or remove additive permissions. | STORY-001, STORY-002, STORY-014 | Team boundary, direct-record access, every privileged action, multi-role users, membership loss. |
| Concurrent lifecycle actions produce conflicting outcomes. | STORY-004, STORY-005, STORY-007, STORY-012 | Submission, proposal decisions, review invalidation, replacement acceptance, archive guard. |
| Replacement operations corrupt immutable history or links. | STORY-007, STORY-008 | Atomic supersession, one active replacement, bidirectional links, no cycles, historical immutability. |
| Tag mutation loses records or breaks discovery. | STORY-009, STORY-010 | Exact filter, all associated-reference updates, historical/archived discovery, record preservation. |
| Comment deletion or Draft deletion removes required evidence. | STORY-011, STORY-013, STORY-015 | Reply preservation, placeholders, audit creation, ordinary-data removal, minimal-event retention. |
| Archival changes lifecycle state or blocks valid later actions. | STORY-012, STORY-013 | Separate archival condition, exact prior-state restoration, restored-Draft deletion. |
| Operational controls are validated below the complete user boundary. | STORY-014, STORY-016 | End-to-end encryption coverage, user-action-to-usable-content timing, actual recovery evidence, browser matrix. |

## Test Traceability Matrix

| Requirement | Acceptance Criterion | Story | Scenario | Test Case | Coverage |
|---|---|---|---|---|---|
| CR-FR-001–002; CR-NFR-001–002 | AC-001 | STORY-001 | TS-001 | TC-001-01–04 | Covered |
| CR-USR-004–006, CR-USR-009–010; CR-FR-009–010; CR-BR-001–002, CR-BR-013, CR-BR-015 | AC-003, AC-006–007, AC-023 | STORY-002 | TS-002 | TC-002-01–05 | Covered |
| CR-FR-003–005, CR-FR-006A, CR-FR-023; CR-BR-010 | AC-002, AC-004, AC-037 | STORY-003 | TS-003 | TC-003-01–03 | Covered |
| CR-FR-006–008, CR-FR-024; CR-BR-003, CR-BR-016 | AC-004–005, AC-024 | STORY-004 | TS-004 | TC-004-01–05 | Covered |
| CR-FR-006–010, CR-FR-014; CR-BR-002–004 | AC-006–008, AC-038 | STORY-005 | TS-005 | TC-005-01–04 | Covered |
| CR-FR-006A, CR-FR-026; CR-BR-011 | AC-014, AC-030 | STORY-006 | TS-006 | TC-006-01–03 | Covered |
| CR-FR-011–013; CR-BR-005–006, CR-BR-013–014 | AC-009–011, AC-025, AC-039 | STORY-007 | TS-007 | TC-007-01–06 | Covered |
| CR-FR-013–014; CR-NFR-003; CR-BR-004–006, CR-BR-009 | AC-012–013, AC-038 | STORY-008 | TS-008 | TC-008-01–04 | Covered |
| CR-FR-005, CR-FR-015–016; CR-BR-009 | AC-001, AC-015 | STORY-009 | TS-009 | TC-009-01–03 | Covered |
| CR-FR-025; CR-BR-017 | AC-029, AC-040–042 | STORY-010 | TS-010 | TC-010-01–05 | Covered |
| CR-FR-017–019; CR-BR-012 | AC-016–019, AC-028 | STORY-011 | TS-011 | TC-011-01–06 | Covered |
| CR-FR-020–021; CR-BR-007, CR-BR-014; CR-NFR-008 | AC-003, AC-020–021, AC-026, AC-034 | STORY-012 | TS-012 | TC-012-01–05 | Covered |
| CR-FR-022; CR-BR-008; CR-NFR-007–008 | AC-022, AC-027, AC-033–034 | STORY-013 | TS-013 | TC-013-01–04 | Covered |
| CR-SCP-003; CR-NFR-001–002, CR-NFR-005 | AC-001, AC-032 | STORY-014 | TS-014 | TC-014-01–02 | Covered |
| CR-FR-014, CR-FR-019–022; CR-NFR-007–008 | AC-013, AC-018, AC-027, AC-033–034 | STORY-015 | TS-015 | TC-015-01–03 | Covered |
| CR-SCP-002; CR-NFR-004, CR-NFR-006, CR-NFR-009, CR-NFR-011 | AC-031, AC-035–036 | STORY-016 | TS-016–018 | TC-016-01–02, TC-017-01, TC-018-01 | Covered |
| CR-NFR-010 | Not applicable: approved scope constraint | STORY-016 | — | — | Covered as constraint; no mandatory test |
| CR-NFR-012 | Not applicable: approved scope constraint | STORY-016 | — | — | Covered as constraint; no mandatory test |

## Business Rule Coverage

| Business Rule | Direct Test Cases | Coverage |
|---|---|---|
| CR-BR-001–002 | TC-002-01, TC-002-04 | Covered |
| CR-BR-003–004 | TC-005-02–03, TC-007-01, TC-008-03 | Covered |
| CR-BR-005–006 | TC-007-01–02, TC-007-05 | Covered |
| CR-BR-007–008 | TC-012-01–03, TC-013-01–03 | Covered |
| CR-BR-009–010 | TC-008-03, TC-009-01, TC-003-03 | Covered |
| CR-BR-011–012 | TC-006-01–02, TC-011-03–04, TC-011-06 | Covered |
| CR-BR-013–014 | TC-007-02–06, TC-012-04 | Covered |
| CR-BR-015–016 | TC-002-05, TC-004-04–05 | Covered |
| CR-BR-017 | TC-010-03–05 | Covered |

## Test Design Gaps and Execution Constraints

- No requirement ambiguity blocks test design.
- Permanent retention cannot be demonstrated by waiting forever. Validation must
  combine observable absence of expiry/permanent-delete behavior with inspection
  of the applicable retention controls and repeated retrieval.
- The supported Chrome and Edge major-version numbers are intentionally resolved
  at execution time because the approved requirement defines them relatively.
- Recovery validation requires an operational backup environment and restoration
  evidence. Absence of that environment would be an execution blocker, not a
  change to expected behavior.
- The performance criterion measures from user initiation until primary content
  is usable. Server response time alone is not sufficient evidence.

## Approved Assumptions and Scope Constraints

- Availability is best effort during business hours with no formal SLA or
  defined schedule; no mandatory availability test is designed.
- Accessibility is best effort with no compliance target or certification;
  no mandatory accessibility conformance test is designed.
- Out-of-scope capabilities CR-OOS-001 through CR-OOS-013 are scope guardrails
  and do not introduce positive product behavior into these cases.

## Open Testing Questions

None. Technical selection of test entry points, data setup, concurrency tooling,
encryption evidence, performance instrumentation, and recovery environment is
deferred to VALIDATION MODE without changing expected behavior.

## Quality Gate

- All 42 approved Acceptance Criteria have been evaluated and covered.
- All 17 explicit Business Rules have direct coverage.
- Every STORY-001 through STORY-016 has at least one scenario and concrete cases.
- Happy, negative, boundary, business-rule, state-transition, acceptance,
  integration, selected E2E, regression, and approved non-functional risks are
  covered where applicable.
- Expected results are observable and do not depend on production implementation
  details.
- Requirement to Acceptance Criterion to Story to Scenario to Test Case
  traceability is preserved.

**Recommendation:** READY FOR HUMAN REVIEW
