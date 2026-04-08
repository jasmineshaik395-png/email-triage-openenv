"""
Tests – verify the environment works correctly before submission.
Run with: python tests/test_env.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import EmailTriageEnv
from graders.graders import grade_easy, grade_medium, grade_hard, run_episode


def test_reset():
    """reset() returns a valid observation."""
    for task in ["easy", "medium", "hard"]:
        env = EmailTriageEnv(task=task)
        obs = env.reset()
        assert "current_email" in obs, f"[{task}] Missing current_email in obs"
        assert "instructions" in obs, f"[{task}] Missing instructions in obs"
        assert obs["task_name"] == task
        print(f"  ✅ reset() OK for task={task}")


def test_step_easy():
    """step() works for easy task."""
    env = EmailTriageEnv(task="easy")
    obs = env.reset()
    action = {"action_type": "classify", "category": "urgent", "reason": "test"}
    obs, reward, done, info = env.step(action)
    assert 0.0 <= reward <= 1.0, "Reward out of range"
    assert "reward_breakdown" in info
    print(f"  ✅ step() OK for easy | reward={reward}")


def test_step_medium():
    """step() works for medium task."""
    env = EmailTriageEnv(task="medium")
    obs = env.reset()
    action = {
        "action_type": "classify",
        "category": "urgent",
        "priority": "high",
        "reason": "test",
    }
    obs, reward, done, info = env.step(action)
    assert 0.0 <= reward <= 1.0
    print(f"  ✅ step() OK for medium | reward={reward}")


def test_step_hard():
    """step() works for hard task."""
    env = EmailTriageEnv(task="hard")
    obs = env.reset()
    action = {
        "action_type": "respond",
        "category": "urgent",
        "priority": "high",
        "response_text": "Dear customer, I sincerely apologize for the inconvenience. We will resolve this immediately. Best regards.",
        "reason": "test",
    }
    obs, reward, done, info = env.step(action)
    assert 0.0 <= reward <= 1.0
    print(f"  ✅ step() OK for hard | reward={reward}")


def test_full_episode():
    """Full episode runs to completion."""
    def dummy_agent(obs):
        task = obs.get("task_name", "easy")
        action = {"action_type": "classify", "category": "normal", "reason": "test"}
        if task in ("medium", "hard"):
            action["priority"] = "medium"
        if task == "hard":
            action["action_type"] = "respond"
            action["response_text"] = "Thank you for reaching out. We will look into this. Best regards."
        return action

    for task in ["easy", "medium", "hard"]:
        result = run_episode(task, dummy_agent)
        assert 0.0 <= result["final_score"] <= 1.0
        assert result["total_steps"] > 0
        print(f"  ✅ Full episode OK for {task} | score={result['final_score']:.3f}")


def test_state():
    """state() returns valid snapshot."""
    env = EmailTriageEnv(task="easy")
    env.reset()
    s = env.state()
    assert "task" in s
    assert "current_index" in s
    assert "done" in s
    print(f"  ✅ state() OK | keys={list(s.keys())}")


def test_done_flag():
    """done=True after all emails processed."""
    env = EmailTriageEnv(task="easy")
    env.reset()
    done = False
    steps = 0
    while not done:
        _, _, done, _ = env.step({"action_type": "classify", "category": "normal"})
        steps += 1
        assert steps < 100, "Infinite loop detected!"
    print(f"  ✅ done=True after {steps} steps (expected 8)")


def test_invalid_action():
    """Invalid action doesn't crash the environment."""
    env = EmailTriageEnv(task="easy")
    env.reset()
    obs, reward, done, info = env.step({"action_type": "classify"})  # missing category
    assert reward >= 0.0  # should not crash
    print(f"  ✅ Invalid action handled gracefully | reward={reward}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Running Environment Tests")
    print("="*50 + "\n")

    tests = [
        test_reset,
        test_step_easy,
        test_step_medium,
        test_step_hard,
        test_full_episode,
        test_state,
        test_done_flag,
        test_invalid_action,
    ]

    passed = 0
    failed = 0
    for test in tests:
        print(f"Running {test.__name__}...")
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")

    if failed > 0:
        sys.exit(1)
