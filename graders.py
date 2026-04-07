"""
Agent Graders – one per task.
Each grader runs the agent through the full episode and returns a final score 0.0–1.0.
These are the "judges" that evaluate agent performance.
"""

from typing import Callable, Dict, Any
from env.environment import EmailTriageEnv


def run_episode(task: str, agent_fn: Callable[[Dict], Dict]) -> Dict[str, Any]:
    """
    Run a full episode for a given task using the provided agent function.

    agent_fn: takes an observation dict, returns an action dict.
    Returns: summary dict with final_score, per_email_scores, transcript.
    """
    env = EmailTriageEnv(task=task)
    obs = env.reset()

    transcript = []
    total_reward = 0.0
    steps = 0

    while True:
        action = agent_fn(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1

        transcript.append({
            "step": steps,
            "email_id": info.get("email_id"),
            "score": reward,
            "breakdown": info.get("reward_breakdown", {}),
        })

        if done:
            break

    final_score = round(total_reward / steps, 4) if steps > 0 else 0.0

    return {
        "task": task,
        "final_score": final_score,
        "total_steps": steps,
        "transcript": transcript,
        "passed": final_score >= PASS_THRESHOLD[task],
    }


# Minimum passing scores per task
PASS_THRESHOLD = {
    "easy":   0.70,
    "medium": 0.55,
    "hard":   0.40,
}


# ──────────────────────────────────────────────
# Individual grader functions (for openenv validate)
# ──────────────────────────────────────────────

def grade_easy(agent_fn: Callable[[Dict], Dict]) -> float:
    """
    Easy task grader.
    Agent must correctly classify emails as urgent/important/normal/spam.
    Passing score: >= 0.70
    """
    result = run_episode("easy", agent_fn)
    return result["final_score"]


def grade_medium(agent_fn: Callable[[Dict], Dict]) -> float:
    """
    Medium task grader.
    Agent must correctly classify AND prioritize emails.
    Passing score: >= 0.55
    """
    result = run_episode("medium", agent_fn)
    return result["final_score"]


def grade_hard(agent_fn: Callable[[Dict], Dict]) -> float:
    """
    Hard task grader.
    Agent must classify, prioritize, AND write appropriate replies.
    Passing score: >= 0.40
    """
    result = run_episode("hard", agent_fn)
    return result["final_score"]


def grade_all(agent_fn: Callable[[Dict], Dict]) -> Dict[str, float]:
    """Run all 3 graders and return scores."""
    return {
        "easy":   grade_easy(agent_fn),
        "medium": grade_medium(agent_fn),
        "hard":   grade_hard(agent_fn),
    }
