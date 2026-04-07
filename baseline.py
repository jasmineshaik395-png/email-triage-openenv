"""
Baseline Inference Script
=========================
Runs a GPT-4o-mini agent against all 3 tasks and prints reproducible scores.

Usage:
    export OPENAI_API_KEY="sk-..."
    python scripts/baseline.py

The agent uses the OpenAI API to decide what action to take for each email.
"""

import json
import os
import sys

# ── Make sure we can import from project root ──
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from graders.graders import grade_all, run_episode

# ──────────────────────────────────────────────
# Build the LLM-powered agent
# ──────────────────────────────────────────────

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert email triage assistant.
You will be given an email and instructions.
You MUST respond with a valid JSON object and nothing else.

For 'easy' task – return:
{
  "action_type": "classify",
  "category": "<urgent|important|normal|spam>",
  "reason": "<brief reason>"
}

For 'medium' task – return:
{
  "action_type": "classify",
  "category": "<urgent|important|normal|spam>",
  "priority": "<high|medium|low>",
  "reason": "<brief reason>"
}

For 'hard' task – return:
{
  "action_type": "respond",
  "category": "<urgent|important|normal|spam>",
  "priority": "<high|medium|low>",
  "response_text": "<your professional email reply>",
  "reason": "<brief reason>"
}

Always return ONLY valid JSON. No markdown, no explanation outside JSON.
"""


def llm_agent(observation: dict) -> dict:
    """
    LLM-powered agent. Reads the observation, calls GPT, returns an action.
    """
    task = observation.get("task_name", "easy")
    email = observation.get("current_email", {})
    instructions = observation.get("instructions", "")

    user_message = f"""
Task: {task}
Instructions: {instructions}

Email to process:
- From: {email.get('sender', '')}
- Subject: {email.get('subject', '')}
- Body: {email.get('body', '')}
- Has attachment: {email.get('has_attachment', False)}

Respond with the correct JSON action.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0,      # deterministic
            seed=42,            # reproducible
            max_tokens=500,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code blocks if model wraps in them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        action = json.loads(raw)
        return action

    except Exception as e:
        print(f"  ⚠️  LLM error: {e}. Using fallback action.")
        return {"action_type": "classify", "category": "normal", "reason": "fallback"}


# ──────────────────────────────────────────────
# Random baseline (for comparison)
# ──────────────────────────────────────────────

import random

def random_agent(observation: dict) -> dict:
    """Random agent — sets a lower bound baseline."""
    task = observation.get("task_name", "easy")
    categories = ["urgent", "important", "normal", "spam"]
    priorities = ["high", "medium", "low"]

    action = {
        "action_type": "classify",
        "category": random.choice(categories),
        "reason": "random choice",
    }
    if task in ("medium", "hard"):
        action["priority"] = random.choice(priorities)
    if task == "hard":
        action["action_type"] = "respond"
        action["response_text"] = "Thank you for your email. We will get back to you soon."

    return action


# ──────────────────────────────────────────────
# Main runner
# ──────────────────────────────────────────────

def run_baseline():
    print("\n" + "="*60)
    print("  OpenEnv Email Triage – Baseline Evaluation")
    print("="*60)

    tasks = ["easy", "medium", "hard"]

    # ── Random agent scores ──
    print("\n📊 Random Agent (lower bound):")
    random.seed(42)
    for task in tasks:
        result = run_episode(task, random_agent)
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {task.upper():8s} → score: {result['final_score']:.3f}  {status}")

    # ── LLM agent scores ──
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY not set. Skipping LLM baseline.")
        print("   Set it with: export OPENAI_API_KEY='sk-...'")
    else:
        print("\n🤖 LLM Agent (gpt-4o-mini, temp=0, seed=42):")
        for task in tasks:
            print(f"  Running {task} task...", end=" ", flush=True)
            result = run_episode(task, llm_agent)
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"score: {result['final_score']:.3f}  {status}")

            # Print per-email breakdown
            for step in result["transcript"]:
                bd = step["breakdown"]
                print(f"    Email {step['email_id']}: {step['score']:.3f}"
                      f" ({bd.get('explanation', '')})")

    print("\n" + "="*60)
    print("  Evaluation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_baseline()
