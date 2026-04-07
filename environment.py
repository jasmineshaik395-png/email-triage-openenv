"""
OpenEnv Email Triage – Core Environment
Implements the full OpenEnv API: reset() / step() / state()
"""

import copy
from typing import Any, Dict, List, Optional, Tuple

from env.models import (
    Action, ActionType, Email, EmailCategory, EmailPriority,
    Observation, Reward,
)
from env.emails import TASK_1_EMAILS, TASK_2_EMAILS, TASK_3_EMAILS


class EmailTriageEnv:
    """
    A real-world email triage environment for AI agents.

    The agent reads emails one by one and must:
      Task 1 (easy)   – Classify each email (spam / urgent / important / normal)
      Task 2 (medium) – Classify AND set priority (high / medium / low)
      Task 3 (hard)   – Classify, prioritize, AND write a reply

    The agent interacts like this:
        obs          = env.reset()
        obs, r, done = env.step(action)
        snapshot     = env.state()
    """

    TASK_EMAILS = {
        "easy":   TASK_1_EMAILS,
        "medium": TASK_2_EMAILS,
        "hard":   TASK_3_EMAILS,
    }

    TASK_INSTRUCTIONS = {
        "easy": (
            "You are an email assistant. For each email, classify it as one of: "
            "'urgent', 'important', 'normal', or 'spam'. "
            "Use action_type='classify' and set the 'category' field."
        ),
        "medium": (
            "You are an email assistant. For each email, classify it (urgent/important/normal/spam) "
            "AND set its priority (high/medium/low). "
            "Use action_type='classify' and fill both 'category' and 'priority' fields."
        ),
        "hard": (
            "You are an email assistant. For each email: "
            "1) Classify it, 2) Set priority, 3) Write a professional reply. "
            "Use action_type='respond' and fill 'category', 'priority', and 'response_text'."
        ),
    }

    def __init__(self, task: str = "easy"):
        if task not in self.TASK_EMAILS:
            raise ValueError(f"task must be one of: {list(self.TASK_EMAILS.keys())}")

        self.task = task
        self._emails: List[Email] = copy.deepcopy(self.TASK_EMAILS[task])
        self._index = 0
        self._scores: List[float] = []
        self._actions_taken: List[Dict] = []
        self._done = False

    # ──────────────────────────────────────────
    # OpenEnv API  (the 3 required methods)
    # ──────────────────────────────────────────

    def reset(self) -> Dict[str, Any]:
        """Start a fresh episode. Returns the first observation."""
        self._emails = copy.deepcopy(self.TASK_EMAILS[self.task])
        self._index = 0
        self._scores = []
        self._actions_taken = []
        self._done = False
        return self._make_observation().to_dict()

    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        Agent takes an action on the current email.
        Returns: (next_observation, reward_score, done, info)
        """
        if self._done:
            raise RuntimeError("Episode finished. Call reset() to start again.")

        # Parse action safely
        try:
            act = Action(**action)
        except Exception as e:
            # Bad action = small penalty
            reward = Reward(total=0.0, penalty=0.1, explanation=f"Invalid action: {e}")
            return self._make_observation().to_dict(), 0.0, self._done, reward.to_dict()

        # Grade the action against current email
        current_email = self._emails[self._index]
        reward = self._grade_action(act, current_email)

        # Record
        self._scores.append(reward.total)
        self._actions_taken.append({
            "email_id": current_email.email_id,
            "action": action,
            "score": reward.total,
        })

        # Move to next email
        self._index += 1
        self._done = self._index >= len(self._emails)

        # Build next observation (or final state if done)
        if not self._done:
            obs = self._make_observation()
        else:
            # Episode over — show summary
            obs = self._make_final_observation()

        info = {
            "email_id": current_email.email_id,
            "reward_breakdown": reward.to_dict(),
            "emails_remaining": len(self._emails) - self._index,
            "running_avg_score": self._avg_score(),
        }

        return obs.to_dict(), reward.total, self._done, info

    def state(self) -> Dict[str, Any]:
        """Return a full snapshot of the current environment state."""
        return {
            "task": self.task,
            "total_emails": len(self._emails),
            "current_index": self._index,
            "done": self._done,
            "scores_so_far": self._scores,
            "average_score": self._avg_score(),
            "actions_taken": self._actions_taken,
            "current_email": (
                self._emails[self._index].to_dict()
                if not self._done else None
            ),
        }

    # ──────────────────────────────────────────
    # Grading logic (partial rewards!)
    # ──────────────────────────────────────────

    def _grade_action(self, action: Action, email: Email) -> Reward:
        """
        Score the agent's action. Gives PARTIAL credit — not just 0 or 1.
        """
        classification_score = 0.0
        priority_score = 0.0
        response_score = 0.0
        penalty = 0.0

        # ── 1. Classification score (all tasks) ──
        if action.action_type in (ActionType.CLASSIFY, ActionType.RESPOND, ActionType.PRIORITIZE):
            if action.category == email.true_category:
                classification_score = 1.0
            elif self._is_close_category(action.category, email.true_category):
                classification_score = 0.5   # partial credit for near-miss
            else:
                classification_score = 0.0

        # Wrong action type penalty
        if action.action_type == ActionType.SKIP:
            penalty += 0.3   # skipping is bad

        # ── 2. Priority score (medium + hard tasks) ──
        if self.task in ("medium", "hard"):
            if action.priority == email.true_priority:
                priority_score = 1.0
            elif self._is_close_priority(action.priority, email.true_priority):
                priority_score = 0.5
            else:
                priority_score = 0.0

        # ── 3. Response score (hard task only) ──
        if self.task == "hard":
            if action.response_text:
                response_score = self._grade_response(action.response_text, email)
            else:
                penalty += 0.3   # no response on hard task = penalty

        # ── 4. Escalate is valid for urgent emails ──
        if action.action_type == ActionType.ESCALATE:
            if email.true_category == EmailCategory.URGENT:
                classification_score = 0.8   # good call to escalate urgent
            else:
                penalty += 0.2   # escalating non-urgent wastes time

        # ── Combine into final score based on task ──
        if self.task == "easy":
            total = classification_score - penalty
        elif self.task == "medium":
            total = (classification_score * 0.5 + priority_score * 0.5) - penalty
        else:  # hard
            total = (
                classification_score * 0.30
                + priority_score     * 0.30
                + response_score     * 0.40
            ) - penalty

        total = round(max(0.0, min(1.0, total)), 4)

        explanation = self._build_explanation(
            classification_score, priority_score, response_score, penalty, email
        )

        return Reward(
            total=total,
            classification_score=classification_score,
            priority_score=priority_score,
            response_score=response_score,
            penalty=penalty,
            explanation=explanation,
        )

    def _grade_response(self, response_text: str, email: Email) -> float:
        """
        Grade the written response. Uses keyword heuristics.
        In production you'd call an LLM judge here.
        """
        score = 0.0
        text = response_text.lower()
        tone = email.expected_response_tone or "professional"

        # Must be non-trivial length
        if len(response_text.strip()) < 20:
            return 0.1

        # Base score for having a response
        score += 0.3

        # Tone-specific keywords
        tone_keywords = {
            "empathetic": ["sorry", "understand", "apologize", "concern", "help", "support"],
            "professional": ["regarding", "please", "thank", "kindly", "sincerely", "confirm"],
            "friendly": ["happy", "great", "sure", "let me know", "feel free"],
            "brief": [],  # brevity graded by length
        }

        keywords = tone_keywords.get(tone, [])
        matches = sum(1 for kw in keywords if kw in text)
        if keywords:
            score += min(0.4, matches * 0.1)

        # Addresses the sender (personalisation)
        if any(word in text for word in ["hi", "hello", "dear"]):
            score += 0.1

        # Has a closing
        if any(word in text for word in ["regards", "sincerely", "thank you", "best"]):
            score += 0.1

        # Brief tone: shorter is better
        if tone == "brief" and len(response_text) < 200:
            score += 0.3
        elif tone == "brief" and len(response_text) > 400:
            score -= 0.1

        # Handles urgent content appropriately
        if email.true_category == EmailCategory.URGENT:
            if any(word in text for word in ["immediately", "priority", "urgent", "right away", "asap"]):
                score += 0.1

        return round(max(0.0, min(1.0, score)), 4)

    # ──────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────

    def _is_close_category(self, predicted, true) -> bool:
        """Some misclassifications are less wrong than others."""
        close_pairs = [
            (EmailCategory.URGENT, EmailCategory.IMPORTANT),
            (EmailCategory.IMPORTANT, EmailCategory.NORMAL),
        ]
        return (predicted, true) in close_pairs or (true, predicted) in close_pairs

    def _is_close_priority(self, predicted, true) -> bool:
        close_pairs = [
            (EmailPriority.HIGH, EmailPriority.MEDIUM),
            (EmailPriority.MEDIUM, EmailPriority.LOW),
        ]
        return (predicted, true) in close_pairs or (true, predicted) in close_pairs

    def _avg_score(self) -> float:
        if not self._scores:
            return 0.0
        return round(sum(self._scores) / len(self._scores), 4)

    def _make_observation(self) -> Observation:
        email = self._emails[self._index]
        # Hide ground truth from agent
        visible_email = Email(
            email_id=email.email_id,
            sender=email.sender,
            subject=email.subject,
            body=email.body,
            received_at=email.received_at,
            has_attachment=email.has_attachment,
            is_reply=email.is_reply,
        )
        return Observation(
            current_email=visible_email,
            inbox_count=len(self._emails) - self._index - 1,
            processed_count=self._index,
            current_score=self._avg_score(),
            day=self._index + 1,
            task_name=self.task,
            instructions=self.TASK_INSTRUCTIONS[self.task],
        )

    def _make_final_observation(self) -> Observation:
        dummy_email = Email(
            email_id="DONE",
            sender="system",
            subject="Inbox complete!",
            body=f"All emails processed. Final score: {self._avg_score():.2%}",
            received_at="",
        )
        return Observation(
            current_email=dummy_email,
            inbox_count=0,
            processed_count=len(self._emails),
            current_score=self._avg_score(),
            day=len(self._emails),
            task_name=self.task,
            instructions="Episode complete.",
        )

    def _build_explanation(self, cls, pri, res, pen, email) -> str:
        parts = [f"Classification: {cls:.1f}"]
        if self.task in ("medium", "hard"):
            parts.append(f"Priority: {pri:.1f}")
        if self.task == "hard":
            parts.append(f"Response: {res:.1f}")
        if pen > 0:
            parts.append(f"Penalty: -{pen:.1f}")
        parts.append(f"True category: {email.true_category}")
        return " | ".join(parts)
