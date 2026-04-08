"""
inference.py – Baseline agent that calls the live API.
"""
import requests

BASE_URL = "https://skjasmine-email-triage-openenv.hf.space"

def run_episode(task: str = "easy"):
    # Reset
    res = requests.post(f"{BASE_URL}/reset", json={"task": task})
    obs = res.json()["observation"]
    print(f"Starting task: {task}")

    while True:
        # Simple rule-based action
        action = {"action_type": "classify", "category": "normal"}
        res = requests.post(f"{BASE_URL}/step", json={"task": task, "action": action})
        data = res.json()
        print(f"Reward: {data['reward']} | Done: {data['done']}")
        if data["done"]:
            break

    print(f"Final score: {data['observation']['current_score']}")

if __name__ == "__main__":
    run_episode("easy")
