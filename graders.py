"""
Agent Graders - one per task.
Each grader runs the agent through the full episode and returns a final score 0.0-1.0.
"""
from typing import Callable, Dict, Any
from environment import EmailTriageEnv

PASS_THRESHOLD = {
    "easy":   0.70,
    "medium": 0.55,
    "hard":   0.40,
}


def run_episode(task: str, agent_fn: Callable[[Dict], Dict]) -> Dict[str, Any]:
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


def grade_easy(agent_fn: Callable[[Dict], Dict]) -> float:
    result = run_episode("easy", agent_fn)
    return result["final_score"]


def grade_medium(agent_fn: Callable[[Dict], Dict]) -> float:
    result = run_episode("medium", agent_fn)
    return result["final_score"]


def grade_hard(agent_fn: Callable[[Dict], Dict]) -> float:
    result = run_episode("hard", agent_fn)
    return result["final_score"]


def grade_all(agent_fn: Callable[[Dict], Dict]) -> Dict[str, float]:
    return {
        "easy":   grade_easy(agent_fn),
        "medium": grade_medium(agent_fn),
        "hard":   grade_hard(agent_fn),
    }
