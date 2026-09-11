from datetime import date, datetime, timezone
from threading import Lock
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
        if len(set(tags)) != len(tags):
            raise ValueError("tags must be unique")
        return tags

    @field_validator("decision_date")
    @classmethod
    def require_decision_date(cls, value: date | None) -> date | None:
        if value is None:
            raise ValueError("decision date must not be null")
        return value


class DecisionRecord(BaseModel):
    id: str
    status: Literal["Draft", "Proposed", "Accepted", "Rejected", "Superseded"] = (
        "Draft"
    )
    abandoned: bool = False
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


class RecordNotFoundError(Exception):
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

    def get(self, record_id: str) -> DecisionRecord | None:
        with self._lock:
            return self._records.get(record_id)

    def update(
        self,
        record_id: str,
        payload: DecisionRecordUpdate,
        actor: MockIdentity,
    ) -> DecisionRecord:
        updates = payload.model_dump(exclude_unset=True)

        with self._lock:
            record = self._records.get(record_id)
            if record is None:
                raise RecordNotFoundError
            self._require_editable_by_author(record, actor)
            updated = record.model_copy(update=updates)
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
            self._require_editable_by_author(record, actor)

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

    @staticmethod
    def _require_editable_by_author(
        record: DecisionRecord,
        actor: MockIdentity,
    ) -> None:
        if record.abandoned:
            raise RecordActionError(
                "An Abandoned replacement Draft cannot be edited or submitted."
            )
        if record.status != "Draft":
            raise RecordActionError("Only a Draft can be edited or submitted.")
        if record.author.id != actor.id:
            raise PermissionError("Only the Draft author may perform this action.")

    @staticmethod
    def _is_missing(value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, list):
            return not value or any(not item.strip() for item in value)
        return False
