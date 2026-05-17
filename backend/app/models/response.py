from enum import Enum


class NotificationType(str, Enum):
    reminder = "reminder"
    edit_alert = "edit_alert"
    deadline = "deadline"


class NotificationStatus(str, Enum):
    sent = "sent"
    failed = "failed"


class NotificationChannel(str, Enum):
    email = "email"
