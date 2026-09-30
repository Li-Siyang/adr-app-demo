from collections.abc import Iterable
from threading import Lock


class DuplicateTagError(Exception):
    pass


class TagStore:
    def __init__(self) -> None:
        self._tags: set[str] = set()
        self._lock = Lock()

    def create(self, name: str) -> str:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Tag name must not be blank.")

        with self._lock:
            if normalized_name in self._tags:
                raise DuplicateTagError(normalized_name)
            self._tags.add(normalized_name)
        return normalized_name

    def ensure(self, names: Iterable[str]) -> None:
        normalized_names = {name.strip() for name in names}
        if "" in normalized_names:
            raise ValueError("Tag names must not be blank.")

        with self._lock:
            self._tags.update(normalized_names)

    def list(self) -> list[str]:
        with self._lock:
            return sorted(self._tags)
