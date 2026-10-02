from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from pydantic import ValidationError

from app.identities import MOCK_IDENTITIES
from app.records import (
    CommentNotFoundError,
    DecisionCommentCreate,
    DecisionRecordCreate,
    DecisionRecordStore,
    RecordActionError,
    RecordNotFoundError,
)


def create_store_and_record() -> tuple[DecisionRecordStore, str]:
    store = DecisionRecordStore()
    record = store.create(
        DecisionRecordCreate(
            title="Commented decision",
            context="A decision needs discussion.",
            decision="Add top-level comments.",
            rationale="Discussion preserves context.",
            alternatives_considered="No discussion.",
            consequences="Comments remain attached.",
            owner_id="maya-member",
            decision_date=date(2026, 9, 1),
            tags=["discussion"],
        ),
        MOCK_IDENTITIES[0],
    )
    return store, record.id


def test_comment_content_is_trimmed_and_rejected_when_blank() -> None:
    comment = DecisionCommentCreate(content="  Consider the trade-off.  ")

    assert comment.content == "Consider the trade-off."
    with pytest.raises(ValidationError):
        DecisionCommentCreate(content="  ")


def test_add_comment_retains_mock_author_and_timestamp() -> None:
    store, record_id = create_store_and_record()
    payload = DecisionCommentCreate(content="A useful note.")

    comment = store.add_comment(record_id, payload.content, MOCK_IDENTITIES[0])

    assert comment.author == MOCK_IDENTITIES[0]
    assert comment.created_at.tzinfo is not None
    assert store.get(record_id).comments == (comment,)


def test_soft_delete_replaces_content_and_records_one_change() -> None:
    store, record_id = create_store_and_record()
    comment = store.add_comment(
        record_id,
        "Keep the decision rationale.",
        MOCK_IDENTITIES[0],
    )
    changes = []

    deleted = store.soft_delete_comment(
        record_id,
        comment.id,
        MOCK_IDENTITIES[0],
        record_change=lambda record, before, after: changes.append(
            (record.id, before, after)
        ),
    )

    assert deleted.content == "[deleted]"
    assert deleted.deleted
    assert store.get(record_id).comments == (deleted,)
    assert changes == [
        (
            record_id,
            comment,
            deleted,
        )
    ]


def test_non_author_cannot_delete_comment_or_record_a_change() -> None:
    store, record_id = create_store_and_record()
    comment = store.add_comment(record_id, "Author-owned note.", MOCK_IDENTITIES[0])
    changes = []

    with pytest.raises(PermissionError, match="Only the comment author"):
        store.soft_delete_comment(
            record_id,
            comment.id,
            MOCK_IDENTITIES[1],
            record_change=lambda *args: changes.append(args),
        )

    assert store.get(record_id).comments == (comment,)
    assert changes == []


def test_deleted_comment_cannot_be_deleted_again() -> None:
    store, record_id = create_store_and_record()
    comment = store.add_comment(record_id, "One-time deletion.", MOCK_IDENTITIES[0])
    changes = []
    store.soft_delete_comment(
        record_id,
        comment.id,
        MOCK_IDENTITIES[0],
        record_change=lambda *args: changes.append(args),
    )

    with pytest.raises(RecordActionError, match="already been deleted"):
        store.soft_delete_comment(
            record_id,
            comment.id,
            MOCK_IDENTITIES[0],
            record_change=lambda *args: changes.append(args),
        )

    assert len(changes) == 1
    assert store.get(record_id).comments[0].content == "[deleted]"


def test_concurrent_deletions_commit_one_tombstone_and_one_audit_change() -> None:
    store, record_id = create_store_and_record()
    comment = store.add_comment(record_id, "Concurrent deletion.", MOCK_IDENTITIES[0])
    changes = []

    def delete_comment() -> bool:
        try:
            store.soft_delete_comment(
                record_id,
                comment.id,
                MOCK_IDENTITIES[0],
                record_change=lambda *args: changes.append(args),
            )
        except RecordActionError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=8) as executor:
        outcomes = list(executor.map(lambda _: delete_comment(), range(16)))

    assert sum(outcomes) == 1
    assert len(changes) == 1
    assert len(store.get(record_id).comments) == 1
    assert store.get(record_id).comments[0].content == "[deleted]"


def test_failed_audit_recording_does_not_delete_comment() -> None:
    store, record_id = create_store_and_record()
    comment = store.add_comment(record_id, "Retain if audit fails.", MOCK_IDENTITIES[0])

    def fail_audit(*args: object) -> None:
        raise OSError("audit storage unavailable")

    with pytest.raises(OSError, match="audit storage unavailable"):
        store.soft_delete_comment(
            record_id,
            comment.id,
            MOCK_IDENTITIES[0],
            record_change=fail_audit,
        )

    assert store.get(record_id).comments == (comment,)


def test_missing_record_and_comment_are_reported() -> None:
    store, record_id = create_store_and_record()

    with pytest.raises(RecordNotFoundError):
        store.add_comment("missing", "A note.", MOCK_IDENTITIES[0])
    with pytest.raises(RecordNotFoundError):
        store.soft_delete_comment(
            "missing",
            "comment",
            MOCK_IDENTITIES[0],
            record_change=lambda *args: None,
        )
    with pytest.raises(CommentNotFoundError):
        store.soft_delete_comment(
            record_id,
            "missing",
            MOCK_IDENTITIES[0],
            record_change=lambda *args: None,
        )


def test_replacement_record_starts_without_comments_from_original() -> None:
    store, record_id = create_store_and_record()
    store.add_comment(record_id, "Discussion on the original.", MOCK_IDENTITIES[0])
    store.submit(
        record_id,
        MOCK_IDENTITIES[0],
        has_designated_approver=True,
    )
    store.decide(
        record_id,
        "Accepted",
        record_change=lambda *args: None,
    )

    replacement = store.create_replacement(
        record_id,
        MOCK_IDENTITIES[2],
        record_change=lambda record: None,
    )

    assert store.get(record_id).comments[0].content == "Discussion on the original."
    assert replacement.comments == ()
