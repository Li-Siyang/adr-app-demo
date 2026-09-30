"""Developer-owned unit tests for STORY-010 tag registry behavior."""

import pytest

from app.tags import DuplicateTagError, TagStore


def test_created_tag_is_available_for_association() -> None:
    store = TagStore()

    created = store.create("architecture")

    assert created == "architecture"
    assert store.list() == ["architecture"]


def test_tag_names_are_trimmed_and_listed_in_sorted_order() -> None:
    store = TagStore()

    store.create(" governance ")
    store.create("architecture")

    assert store.list() == ["architecture", "governance"]


def test_exact_duplicate_tag_creation_is_rejected() -> None:
    store = TagStore()
    store.create("architecture")

    with pytest.raises(DuplicateTagError):
        store.create("architecture")

    assert store.list() == ["architecture"]


def test_blank_tag_names_are_rejected() -> None:
    store = TagStore()

    with pytest.raises(ValueError, match="must not be blank"):
        store.create("  ")

    assert store.list() == []


def test_associated_record_tags_are_registered_idempotently() -> None:
    store = TagStore()

    store.ensure(["architecture", "governance"])
    store.ensure(["governance", "testing"])

    assert store.list() == ["architecture", "governance", "testing"]
