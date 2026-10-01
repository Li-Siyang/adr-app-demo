from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone
from threading import Lock
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.governance import is_administrator
from app.identities import MockIdentity, find_mock_identity


class DecisionRecordCreate(BaseModel):
    title: str
    context: str
    decision: str
    rationale: str
    alternatives_considered: str
    consequences: str
    owner_id: str
    decision_date: date
    tags: list[str] = Field(min_length=1)

    @field_validator(
        "title",
        "context",
        "decision",
        "rationale",
        "alternatives_considered",
        "consequences",
        "owner_id",
    )
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("tags")
    @classmethod
    def require_non_blank_tags(cls, value: list[str]) -> list[str]:
        tags = [tag.strip() for tag in value]
        if not tags or any(not tag for tag in tags):
            raise ValueError("tags must not be blank")
        if len(set(tags)) != len(tags):
            raise ValueError("tags must be unique")
        return tags


class DecisionRecordUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    context: str | None = None
    decision: str | None = None
    rationale: str | None = None
    alternatives_considered: str | None = None
    consequences: str | None = None
    decision_date: date | None = None
    tags: list[str] | None = None

    @field_validator(
        "title",
        "context",
        "decision",
        "rationale",
        "alternatives_considered",
        "consequences",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("must not be null")
        return value.strip()

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            raise ValueError("tags must not be null")
        tags = [tag.strip() for tag in value]
        if any(not tag for tag in tags):
            raise ValueError("tags must not be blank")
        if len(set(tags)) != len(tags):
            raise ValueError("tags must be unique")
        return tags

    @field_validator("decision_date")
    @classmethod
    def require_decision_date(cls, value: date | None) -> date | None:
        if value is None:
            raise ValueError("decision date must not be null")
        return value


class DecisionCommentCreate(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def require_non_blank_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Comment content must not be blank.")
        return value


class DecisionComment(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    content: str
    author: MockIdentity
    created_at: datetime
    deleted: bool = False


class DecisionRecord(BaseModel):
    id: str
    status: Literal["Draft", "Proposed", "Accepted", "Rejected", "Superseded"] = (
        "Draft"
    )
    abandoned: bool = False
    archived: bool = False
    replaces_record_id: str | None = None
    replacement_record_ids: list[str] = Field(default_factory=list)
    title: str
    context: str
    decision: str
    rationale: str
    alternatives_considered: str
    consequences: str
    author: MockIdentity
    owner: MockIdentity
    decision_date: date
    tags: list[str]
    data_classification_notice: str = (
        "Demo or synthetic data only. Do not enter real internal confidential "
        "information, regulated personal information, or health information."
    )
    created_at: datetime
    comments: tuple[DecisionComment, ...] = ()


class RecordNotFoundError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass


class RecordActionError(Exception):
    pass


class DraftSubmissionError(Exception):
    def __init__(self, missing_fields: list[str], approver_required: bool) -> None:
        self.missing_fields = missing_fields
        self.approver_required = approver_required
        super().__init__("The Draft does not meet the submission requirements.")


class DecisionRecordStore:
    REQUIRED_SUBMISSION_FIELDS = (
        "title",
        "context",
        "decision",
        "rationale",
        "alternatives_considered",
        "consequences",
        "owner",
        "decision_date",
        "tags",
    )

    def __init__(self) -> None:
        self._records: dict[str, DecisionRecord] = {}
        self._lock = Lock()

    def create(
        self,
        payload: DecisionRecordCreate,
        author: MockIdentity,
    ) -> DecisionRecord:
        owner = find_mock_identity(payload.owner_id)
        if owner is None:
            raise ValueError("The selected owner does not exist.")

        record = DecisionRecord(
            id=str(uuid4()),
            title=payload.title,
            context=payload.context,
            decision=payload.decision,
            rationale=payload.rationale,
            alternatives_considered=payload.alternatives_considered,
            consequences=payload.consequences,
            author=author,
            owner=owner,
            decision_date=payload.decision_date,
            tags=payload.tags,
            created_at=datetime.now(timezone.utc),
        )
        with self._lock:
            self._records[record.id] = record
        return record

    def list(self) -> list[DecisionRecord]:
        with self._lock:
            return list(self._records.values())

    def list_by_exact_tag(self, tag: str) -> list[DecisionRecord]:
        with self._lock:
            return [
                record
                for record in self._records.values()
                if tag in record.tags
            ]

    def get(self, record_id: str) -> DecisionRecord | None:
        with self._lock:
            return self._records.get(record_id)

    def add_comment(
        self,
        record_id: str,
        content: str,
        actor: MockIdentity,
    ) -> DecisionComment:
        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError

            comment = DecisionComment(
                id=str(uuid4()),
                content=content,
                author=actor,
                created_at=datetime.now(timezone.utc),
            )
            self._records[record_id] = record.model_copy(
                update={"comments": (*record.comments, comment)}
            )
            return comment

    def soft_delete_comment(
        self,
        record_id: str,
        comment_id: str,
        actor: MockIdentity,
        *,
        record_change: Callable[
            [DecisionRecord, DecisionComment, DecisionComment], None
        ],
    ) -> DecisionComment:
        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError

            comment_index = next(
                (
                    index
                    for index, comment in enumerate(record.comments)
                    if comment.id == comment_id
                ),
                None,
            )
            if comment_index is None:
                raise CommentNotFoundError

            comment = record.comments[comment_index]
            if comment.author.id != actor.id:
                raise PermissionError("Only the comment author may delete it.")
            if comment.deleted:
                raise RecordActionError("The comment has already been deleted.")

            deleted_comment = comment.model_copy(
                update={"content": "[deleted]", "deleted": True}
            )
            updated_comments = list(record.comments)
            updated_comments[comment_index] = deleted_comment
            updated_record = record.model_copy(
                update={"comments": tuple(updated_comments)}
            )
            record_change(record, comment, deleted_comment)
            self._records[record_id] = updated_record
            return deleted_comment

    def update(
        self,
        record_id: str,
        payload: DecisionRecordUpdate,
        actor: MockIdentity,
        *,
        record_change: Callable[[DecisionRecord, DecisionRecord], None] | None = None,
    ) -> DecisionRecord:
        updates = payload.model_dump(exclude_unset=True)

        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError
            self._require_not_archived(record)
            self._require_editable_by_author(record, actor)
            restart_review = record.status == "Proposed" and bool(updates)
            if restart_review:
                updates["status"] = "Draft"
            updated = record.model_copy(update=updates)
            if updates and record_change is not None:
                record_change(record, updated)
            self._records[record_id] = updated
            return updated

    def decide(
        self,
        record_id: str,
        outcome: Literal["Accepted", "Rejected"],
        *,
        record_change: Callable[
            [
                DecisionRecord,
                DecisionRecord,
                tuple[DecisionRecord, DecisionRecord] | None,
            ],
            None,
        ],
    ) -> DecisionRecord:
        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError
            self._require_not_archived(record)
            if record.status != "Proposed":
                raise RecordActionError(
                    "Only a Proposed record can be accepted or rejected."
                )

            superseded_transition = None
            if outcome == "Accepted" and record.replaces_record_id is not None:
                original = self._records.get(record.replaces_record_id)
                if (
                    original is None
                    or original.status != "Accepted"
                    or original.archived
                    or record.id not in original.replacement_record_ids
                ):
                    raise RecordActionError(
                        "The original Accepted record is no longer eligible "
                        "for replacement acceptance."
                    )
                superseded = original.model_copy(
                    update={"status": "Superseded"}
                )
                superseded_transition = (original, superseded)

            decided = record.model_copy(update={"status": outcome})
            record_change(record, decided, superseded_transition)
            if superseded_transition is not None:
                original, superseded = superseded_transition
                self._records[original.id] = superseded
            self._records[record_id] = decided
            return decided

    def create_replacement(
        self,
        record_id: str,
        actor: MockIdentity,
        *,
        record_change: Callable[[DecisionRecord], None],
    ) -> DecisionRecord:
        with self._lock:
            original = self._records.get(record_id)
            if original is None:
                raise RecordNotFoundError
            if not is_administrator(actor):
                raise PermissionError(
                    "Only an administrator may create a replacement version."
                )
            self._require_not_archived(original)
            if original.status != "Accepted":
                raise RecordActionError(
                    "Only an Accepted record can have a replacement version."
                )
            if any(
                (replacement := self._records.get(replacement_id)) is not None
                and replacement.status in ("Draft", "Proposed")
                and not replacement.abandoned
                for replacement_id in original.replacement_record_ids
            ):
                raise RecordActionError(
                    "An active replacement version already exists."
                )

            replacement = original.model_copy(
                update={
                    "id": str(uuid4()),
                    "status": "Draft",
                    "abandoned": False,
                    "replaces_record_id": original.id,
                    "replacement_record_ids": [],
                    "author": actor,
                    "tags": list(original.tags),
                    "created_at": datetime.now(timezone.utc),
                    "comments": (),
                }
            )
            updated_original = original.model_copy(
                update={
                    "replacement_record_ids": [
                        *original.replacement_record_ids,
                        replacement.id,
                    ]
                }
            )
            record_change(replacement)
            self._records[original.id] = updated_original
            self._records[replacement.id] = replacement
            return replacement

    def abandon_replacement(
        self,
        record_id: str,
        actor: MockIdentity,
        *,
        record_change: Callable[[DecisionRecord, DecisionRecord], None],
    ) -> DecisionRecord:
        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError
            if not is_administrator(actor):
                raise PermissionError(
                    "Only an administrator may abandon a replacement Draft."
                )
            self._require_not_archived(record)
            if (
                record.status != "Draft"
                or record.abandoned
                or record.replaces_record_id is None
            ):
                raise RecordActionError(
                    "Only an active replacement Draft can be abandoned."
                )
            original = self._records.get(record.replaces_record_id)
            if (
                original is None
                or original.status != "Accepted"
                or record.id not in original.replacement_record_ids
            ):
                raise RecordActionError(
                    "The original Accepted record is no longer eligible "
                    "for replacement abandonment."
                )

            abandoned = record.model_copy(update={"abandoned": True})
            record_change(record, abandoned)
            self._records[record_id] = abandoned
            return abandoned

    def transfer_owner(
        self,
        record_id: str,
        owner_id: str,
        actor: MockIdentity,
        *,
        record_change: Callable[[DecisionRecord, DecisionRecord], None],
    ) -> DecisionRecord:
        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError
            self._require_not_archived(record)
            if record.abandoned or record.status not in ("Draft", "Proposed"):
                raise RecordActionError(
                    "Only a non-Abandoned Draft or Proposed record can change owner."
                )
            if actor.id not in (record.author.id, record.owner.id) and not (
                is_administrator(actor)
            ):
                raise PermissionError(
                    "Only the author, owner, or an administrator may transfer ownership."
                )
            owner = find_mock_identity(owner_id)
            if owner is None:
                raise ValueError("The selected owner does not exist.")
            if owner.id == record.owner.id:
                raise RecordActionError(
                    "Select a different owner to transfer ownership."
                )
            updated = record.model_copy(update={"owner": owner})
            record_change(record, updated)
            self._records[record_id] = updated
            return updated

    def submit(
        self,
        record_id: str,
        actor: MockIdentity,
        *,
        has_designated_approver: bool,
    ) -> DecisionRecord:
        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError
            self._require_not_archived(record)
            if record.status != "Draft":
                if record.status == "Rejected":
                    raise RecordActionError("Rejected records are immutable.")
                raise RecordActionError("Only a Draft can be submitted.")
            self._require_editable_by_author(record, actor)
            if record.replaces_record_id is not None:
                original = self._records.get(record.replaces_record_id)
                if original is not None and original.archived:
                    raise RecordActionError(
                        "Restore the original before submitting its replacement."
                    )

            missing_fields = [
                field
                for field in self.REQUIRED_SUBMISSION_FIELDS
                if self._is_missing(getattr(record, field))
            ]
            if missing_fields or not has_designated_approver:
                raise DraftSubmissionError(
                    missing_fields=missing_fields,
                    approver_required=not has_designated_approver,
                )

            proposed = record.model_copy(update={"status": "Proposed"})
            self._records[record_id] = proposed
            return proposed

    def set_archived(
        self,
        record_id: str,
        actor: MockIdentity,
        *,
        archived: bool,
        record_change: Callable[[DecisionRecord, DecisionRecord], None],
    ) -> DecisionRecord:
        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError
            if not is_administrator(actor):
                raise PermissionError(
                    "Only an administrator may archive or restore a record."
                )
            if record.archived == archived:
                raise RecordActionError(
                    "The record is already archived." if archived
                    else "The record is not archived."
                )
            if archived and record.status == "Accepted" and any(
                (replacement := self._records.get(replacement_id)) is not None
                and replacement.status == "Proposed"
                and not replacement.abandoned
                for replacement_id in record.replacement_record_ids
            ):
                raise RecordActionError(
                    "An Accepted original with an active Proposed replacement "
                    "cannot be archived."
                )
            updated = record.model_copy(update={"archived": archived})
            record_change(record, updated)
            self._records[record_id] = updated
            return updated

    @staticmethod
    def _require_not_archived(record: DecisionRecord) -> None:
        if record.archived:
            raise RecordActionError("Restore the archived record before changing it.")

    @staticmethod
    def _require_editable_by_author(
        record: DecisionRecord,
        actor: MockIdentity,
    ) -> None:
        if record.abandoned:
            raise RecordActionError(
                "An Abandoned replacement Draft cannot be edited or submitted."
            )
        if record.status == "Rejected":
            raise RecordActionError("Rejected records are immutable.")
        if record.status not in ("Draft", "Proposed"):
            raise RecordActionError("Only a Draft or Proposed record can be edited.")
        if record.author.id != actor.id:
            raise PermissionError(
                "Only the record author may edit a Draft or Proposed record."
            )

    @staticmethod
    def _is_missing(value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, list):
            return not value or any(not item.strip() for item in value)
        return False
