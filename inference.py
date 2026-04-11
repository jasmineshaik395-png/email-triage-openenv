"""
inference.py – Baseline agent that runs the environment locally.
"""
from environment import EmailTriageEnv

def run_episode(task: str = "easy"):
    env = EmailTriageEnv(task=task)
    obs = env.reset()
    print(f"Starting task: {task}")

    while True:
        action = {"action_type": "classify", "category": "normal"}
        obs, reward, done, info = env.step(action)
        print(f"Reward: {reward:.3f} | Done: {done}")
        if done:
            break

    print(f"Final score: {obs['current_score']:.3f}")

if __name__ == "__main__":
    run_episode("easy")
