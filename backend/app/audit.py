from collections.abc import Iterable
from datetime import datetime, timezone
from enum import StrEnum
import json
from pathlib import Path
import sqlite3
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
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    actor_display_name TEXT NOT NULL,
                    actor_roles TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    subject_type TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    changes TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> AuditEvent:
        return AuditEvent(
            id=row["id"],
            event_type=row["event_type"],
            actor=AuditActor(
                id=row["actor_id"],
                display_name=row["actor_display_name"],
                roles=tuple(Role(role) for role in json.loads(row["actor_roles"])),
            ),
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            subject_type=row["subject_type"],
            subject_id=row["subject_id"],
            changes=tuple(
                AuditChange.model_validate(change)
                for change in json.loads(row["changes"])
            ),
        )

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
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    id,
                    event_type,
                    actor_id,
                    actor_display_name,
                    actor_roles,
                    occurred_at,
                    subject_type,
                    subject_id,
                    changes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.event_type.value,
                    event.actor.id,
                    event.actor.display_name,
                    json.dumps([role.value for role in event.actor.roles]),
                    event.occurred_at.isoformat(),
                    event.subject_type,
                    event.subject_id,
                    json.dumps(
                        [
                            change.model_dump(mode="json")
                            for change in event.changes
                        ]
                    ),
                ),
            )
        return event

    def list(
        self,
        *,
        subject_type: str | None = None,
        subject_id: str | None = None,
    ) -> tuple[AuditEvent, ...]:
        filters: list[str] = []
        values: list[str] = []
        if subject_type is not None:
            filters.append("subject_type = ?")
            values.append(subject_type)
        if subject_id is not None:
            filters.append("subject_id = ?")
            values.append(subject_id)

        query = "SELECT * FROM audit_events"
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY sequence"
        with self._connect() as connection:
            rows = connection.execute(query, values).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def get(self, event_id: str) -> AuditEvent | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM audit_events WHERE id = ?",
                (event_id,),
            ).fetchone()
        return self._from_row(row) if row is not None else None
