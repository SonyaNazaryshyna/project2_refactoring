"""Username value object — immutable and self-validating."""

from __future__ import annotations
import re
from dataclasses import dataclass

from src.domain.exceptions import DomainException

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self) -> None:
        if not _USERNAME_RE.match(self.value):
            raise DomainException("Username must be 3-30 characters and contain only letters, digits, or underscores.")

    def __str__(self) -> str:
        return self.value
