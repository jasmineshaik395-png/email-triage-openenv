"""
OpenEnv Email Triage - Typed Models (stdlib only)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EmailCategory(str, Enum):
    URGENT    = "urgent"
    IMPORTANT = "important"
    NORMAL    = "normal"
    SPAM      = "spam"


class EmailPriority(str, Enum):
    HIGH   = "high"
    MEDIUM = "medium"
    LOW    = "low"


class ActionType(str, Enum):
    CLASSIFY   = "classify"
    PRIORITIZE = "prioritize"
    RESPOND    = "respond"
    SKIP       = "skip"
    ESCALATE   = "escalate"


@dataclass
class Email:
    email_id: str
    sender: str
    subject: str
    body: str
    received_at: str
    has_attachment: bool = False
    is_reply: bool = False
    true_category: Optional[str] = None
    true_priority: Optional[str] = None
    expected_response_tone: Optional[str] = None

    def to_dict(self):
        return {
            "email_id": self.email_id,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "received_at": self.received_at,
            "has_attachment": self.has_attachment,
            "is_reply": self.is_reply,
        }


@dataclass
class Action:
    action_type: str
    category: Optional[str] = None
    priority: Optional[str] = None
    response_text: Optional[str] = None
    reason: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Action":
        return cls(
            action_type=d.get("action_type", "skip"),
            category=d.get("category"),
            priority=d.get("priority"),
            response_text=d.get("response_text"),
            reason=d.get("reason"),
        )

    def is_valid(self) -> bool:
        return self.action_type in {e.value for e in ActionType}


@dataclass
class Observation:
    current_email: Email
    inbox_count: int
    processed_count: int
    current_score: float
    day: int
    task_name: str
    instructions: str

    def to_dict(self):
        return {
            "current_email": self.current_email.to_dict(),
            "inbox_count": self.inbox_count,
            "processed_count": self.processed_count,
            "current_score": self.current_score,
            "day": self.day,
            "task_name": self.task_name,
            "instructions": self.instructions,
        }


@dataclass
class Reward:
    total: float
    classification_score: float = 0.0
    priority_score: float = 0.0
    response_score: float = 0.0
    penalty: float = 0.0
    explanation: str = ""

    def to_dict(self):
        return {
            "total": self.total,
            "classification_score": self.classification_score,
            "priority_score": self.priority_score,
            "response_score": self.response_score,
            "penalty": self.penalty,
            "explanation": self.explanation,
        }
