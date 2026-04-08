"""
Quick demo – shows the environment working end-to-end.
Run with: python demo.py
No API key needed – uses a simple rule-based agent.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import EmailTriageEnv


def rule_based_agent(obs: dict) -> dict:
    """
    Simple rule-based agent — reads keywords to decide action.
    Not perfect, but shows how an agent interacts with the environment.
    """
    email = obs["current_email"]
    subject = (email["subject"] or "").lower()
    body    = (email["body"] or "").lower()
    task    = obs["task_name"]
    text    = subject + " " + body

    # Classify
    if any(w in text for w in ["urgent", "immediately", "asap", "crash", "down", "emergency", "warning", "alert", "deadline", "overdue"]):
        category = "urgent"
        priority = "high"
    elif any(w in text for w in ["meeting", "contract", "review", "discuss", "proposal", "invite", "collaboration"]):
        category = "important"
        priority = "medium"
    elif any(w in text for w in ["free", "winner", "prize", "click here", "unsubscribe", "offer", "deal", "50% off"]):
        category = "spam"
        priority = "low"
    else:
        category = "normal"
        priority = "low"

    action = {
        "action_type": "classify",
        "category": category,
        "reason": "keyword-based rule",
    }

    if task in ("medium", "hard"):
        action["priority"] = priority

    if task == "hard":
        action["action_type"] = "respond"
        # Write a simple tone-matched response
        sender_name = email["sender"].split("@")[0].replace(".", " ").title()
        if category == "urgent":
            action["response_text"] = (
                f"Dear {sender_name},\n\n"
                "Thank you for reaching out. I completely understand the urgency of this situation "
                "and I sincerely apologize for any inconvenience caused. "
                "I am treating this as our top priority and will personally ensure it is resolved immediately.\n\n"
                "Please expect an update from us within the next hour.\n\n"
                "Best regards"
            )
        elif category == "important":
            action["response_text"] = (
                f"Dear {sender_name},\n\n"
                "Thank you for your email. I appreciate you reaching out regarding this matter. "
                "I will review this carefully and get back to you with a full response shortly.\n\n"
                "Kind regards"
            )
        else:
            action["response_text"] = (
                f"Hi {sender_name},\n\n"
                "Thanks for your message! I've received it and will follow up as needed.\n\n"
                "Best"
            )

    return action


def run_demo():
    print("\n" + "="*55)
    print("  📧  OpenEnv Email Triage — Live Demo")
    print("="*55)

    for task in ["easy", "medium", "hard"]:
        print(f"\n{'─'*55}")
        print(f"  TASK: {task.upper()}")
        print(f"{'─'*55}")

        env = EmailTriageEnv(task=task)
        obs = env.reset()

        print(f"  Instructions: {obs['instructions'][:80]}...")
        print(f"  Emails in inbox: {obs['inbox_count'] + 1}\n")

        step = 0
        while True:
            email = obs["current_email"]
            print(f"  [{step+1}] From: {email['sender']}")
            print(f"       Subject: {email['subject']}")

            action = rule_based_agent(obs)
            obs, reward, done, info = env.step(action)

            bd = info["reward_breakdown"]
            print(f"       → Classified as: {action.get('category','?').upper()}"
                  + (f" | Priority: {action.get('priority','?')}" if task != "easy" else "")
                  + f" | Score: {reward:.2f}")
            if task == "hard" and action.get("response_text"):
                preview = action["response_text"][:60].replace("\n", " ")
                print(f"       → Response: \"{preview}...\"")

            step += 1
            if done:
                break

        final = obs["current_score"]
        print(f"\n  ✅ Task '{task}' complete — Final Score: {final:.3f} / 1.000")

    print("\n" + "="*55)
    print("  Demo complete! See README for full docs.")
    print("="*55 + "\n")


if __name__ == "__main__":
    run_demo()
