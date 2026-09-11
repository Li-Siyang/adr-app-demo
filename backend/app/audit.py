from collections.abc import Iterable
from datetime import datetime, timezone
from enum import StrEnum
from threading import Lock
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.identities import MockIdentity, Role


class AuditEventType(StrEnum):
    USER_ROLE_CHANGED = "user_role_changed"
    APPROVER_DESIGNATION_CHANGED = "approver_designation_changed"
    LIFECYCLE_TRANSITIONED = "lifecycle_transitioned"
    REPLACEMENT_DRAFT_ABANDONED = "replacement_draft_abandoned"
    RECORD_ARCHIVED = "record_archived"
    RECORD_RESTORED = "record_restored"
    OWNERSHIP_TRANSFERRED = "ownership_transferred"
    COMMENT_DELETED = "comment_deleted"


class AuditChange(BaseModel):
    model_config = ConfigDict(frozen=True)

    field: str = Field(min_length=1)
    before: str | bool | None
    after: str | bool | None

    @model_validator(mode="after")
    def require_changed_value(self) -> "AuditChange":
        if self.before == self.after:
            raise ValueError("audit change must contain different values")
        return self


class AuditActor(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    display_name: str
    roles: tuple[Role, ...]


class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    event_type: AuditEventType
    actor: AuditActor
    occurred_at: datetime
    subject_type: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    changes: tuple[AuditChange, ...] = Field(min_length=1)


class AuditEventStore:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._events_by_id: dict[str, AuditEvent] = {}
        self._lock = Lock()

    def record(
        self,
        *,
        event_type: AuditEventType,
        actor: MockIdentity,
        subject_type: str,
        subject_id: str,
        changes: Iterable[AuditChange],
    ) -> AuditEvent:
        event = AuditEvent(
            id=str(uuid4()),
            event_type=event_type,
            actor=AuditActor(
                id=actor.id,
                display_name=actor.display_name,
                roles=actor.roles,
            ),
            occurred_at=datetime.now(timezone.utc),
            subject_type=subject_type,
            subject_id=subject_id,
            changes=tuple(changes),
        )
        with self._lock:
            self._events.append(event)
            self._events_by_id[event.id] = event
        return event

    def list(
        self,
        *,
        subject_type: str | None = None,
        subject_id: str | None = None,
    ) -> tuple[AuditEvent, ...]:
        with self._lock:
            events = tuple(self._events)
        if subject_type is not None:
            events = tuple(
                event for event in events if event.subject_type == subject_type
            )
        if subject_id is not None:
            events = tuple(event for event in events if event.subject_id == subject_id)
        return events

    def get(self, event_id: str) -> AuditEvent | None:
        with self._lock:
            return self._events_by_id.get(event_id)
