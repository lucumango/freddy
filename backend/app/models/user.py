from enum import Enum


class UserRole(str, Enum):
    participant = "participant"
    admin = "admin"
