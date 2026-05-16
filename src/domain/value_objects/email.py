"""Email value object — immutable and self-validating."""
from __future__ import annotations
import re
from dataclasses import dataclass

from src.domain.exceptions import DomainException

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise DomainException(f"Email format is invalid: {self.value!r}")

    def __str__(self) -> str:
        return self.value
