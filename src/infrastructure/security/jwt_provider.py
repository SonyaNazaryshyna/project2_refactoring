"""JWT Provider — infrastructure security."""
from __future__ import annotations
from datetime import datetime, timezone
from dataclasses import dataclass

from src.application.dtos import TokenResponse

# Імпортуємо через importlib щоб уникнути конфлікту з файлом jwt.py
import importlib
_jwt = importlib.import_module("jwt")


@dataclass
class JWTConfig:
    secret: str
    algorithm: str
    access_ttl_seconds: int
    refresh_ttl_seconds: int


class JWTProvider:
    def __init__(self, config: JWTConfig) -> None:
        self._cfg = config

    def create_tokens(self, user_id: str, role: str) -> TokenResponse:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        access_payload = {
            "sub": user_id, "role": role, "type": "access",
            "iat": now_ts, "exp": now_ts + self._cfg.access_ttl_seconds,
        }
        refresh_payload = {
            "sub": user_id, "type": "refresh",
            "iat": now_ts, "exp": now_ts + self._cfg.refresh_ttl_seconds,
        }
        access  = _jwt.encode(access_payload,  self._cfg.secret, algorithm=self._cfg.algorithm)
        refresh = _jwt.encode(refresh_payload, self._cfg.secret, algorithm=self._cfg.algorithm)
        return TokenResponse(access_token=access, refresh_token=refresh)

    def decode(self, token: str) -> dict:
        return _jwt.decode(token, self._cfg.secret, algorithms=[self._cfg.algorithm])
