"""
inference.py - Baseline agent that runs the environment via API.
"""
import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://skjasmine-email-triage-openenv.hf.space")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline")
HF_TOKEN = os.getenv("HF_TOKEN")

headers = {}
if HF_TOKEN:
    headers["Authorization"] = f"Bearer {HF_TOKEN}"


def reset(task: str = "easy"):
    response = requests.post(
        f"{API_BASE_URL}/reset",
        json={"task": task},
        headers=headers,
    )
    return response.json()


def step(task: str, action: dict):
    response = requests.post(
        f"{API_BASE_URL}/step",
        json={"task": task, "action": action},
        headers=headers,
    )
    return response.json()


def run_episode(task: str = "easy"):
    print(f"Starting task: {task}")
    print(f"API_BASE_URL: {API_BASE_URL}")
    print(f"MODEL_NAME: {MODEL_NAME}")

    result = reset(task)
    obs = result.get("observation", {})

    total_reward = 0.0
    steps = 0

    while True:
        action = {"action_type": "classify", "category": "normal"}
        result = step(task, action)

        reward = result.get("reward", 0.0)
        done = result.get("done", False)
        obs = result.get("observation", {})

        total_reward += reward
        steps += 1

        print(f"Step {steps} | Reward: {reward:.3f} | Done: {done}")

        if done:
            break

    final_score = total_reward / steps if steps > 0 else 0.0
    print(f"Final score: {final_score:.3f}")
    return final_score


if __name__ == "__main__":
    run_episode("easy")
