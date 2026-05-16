"""AuthService — orchestrates registration and login use cases."""

from __future__ import annotations

from src.application.dtos import LoginRequest, RegisterRequest, TokenResponse
from src.domain.entities.user import User
from src.domain.ports import UserRepository, NotificationSender
from src.infrastructure.security.password import PasswordEncoder
from src.infrastructure.security.jwt_provider import JWTProvider


class AuthenticationError(Exception):
    pass


class ConflictError(Exception):
    pass


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        password_encoder: PasswordEncoder,
        jwt_provider: JWTProvider,
        notification_sender: NotificationSender,
    ) -> None:
        self._users = user_repo
        self._pw = password_encoder
        self._jwt = jwt_provider
        self._notify = notification_sender

    def register(self, req: RegisterRequest) -> TokenResponse:
        if self._users.exists_by_email(req.email):
            raise ConflictError("Email is already taken.")
        if self._users.exists_by_username(req.username):
            raise ConflictError("Username is already taken.")

        hashed = self._pw.hash(req.password)
        user = User.create(
            username=req.username,
            email=req.email,
            password_hash=hashed,
            bio=req.bio,
        )
        self._users.save(user)
        self._notify.send_welcome(user)

        return self._jwt.create_tokens(str(user.id), role="ROLE_USER")

    def login(self, req: LoginRequest) -> TokenResponse:
        user = self._users.find_by_email(req.email)
        if user is None or not self._pw.verify(req.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("Account is deactivated.")

        return self._jwt.create_tokens(str(user.id), role="ROLE_USER")
