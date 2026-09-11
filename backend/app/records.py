from datetime import date, datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

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


class DecisionRecord(BaseModel):
    id: str
    status: str = "Draft"
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


class DecisionRecordStore:
    def __init__(self) -> None:
        self._records: dict[str, DecisionRecord] = {}

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
        self._records[record.id] = record
        return record

    def list(self) -> list[DecisionRecord]:
        return list(self._records.values())

    def get(self, record_id: str) -> DecisionRecord | None:
        return self._records.get(record_id)
