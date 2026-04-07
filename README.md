# 📧 OpenEnv Email Triage

A **real-world AI agent environment** built on the OpenEnv standard. AI agents learn to triage emails — classifying, prioritizing, and responding to them — just like a human support agent would.

---

## 🌍 Why Email Triage?

Email triage is something millions of humans do every day at work. It requires:
- **Understanding context** (is this urgent or spam?)
- **Prioritization** (what needs attention first?)
- **Communication** (writing professional replies)

This makes it a rich, realistic benchmark for language-model-based agents.

---

## 🗂️ Project Structure

```
email-triage-openenv/
├── env/
│   ├── __init__.py          # Package exports
│   ├── models.py            # Typed dataclasses (Email, Action, Observation, Reward)
│   ├── emails.py            # Dataset of emails for all 3 tasks
│   └── environment.py       # Core env: reset() / step() / state()
├── graders/
│   └── graders.py           # Task graders (easy / medium / hard)
├── scripts/
│   └── baseline.py          # LLM baseline inference script
├── tests/
│   └── test_env.py          # Environment tests (8 tests)
├── app.py                   # FastAPI server for HF Spaces
├── openenv.yaml             # OpenEnv spec metadata
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🎮 Environment Description

The agent processes emails one by one from an inbox. For each email, it takes an action. The environment scores the action and returns the next email.

```
┌─────────────┐     observation      ┌───────────┐
│             │ ──────────────────►  │           │
│  Environment│                      │   Agent   │
│             │ ◄──────────────────  │           │
└─────────────┘        action        └───────────┘
       │
       ▼
   reward (0.0–1.0)
```

---

## 📐 Observation Space

What the agent **sees** at each step:

| Field | Type | Description |
|---|---|---|
| `current_email.email_id` | string | Unique email ID |
| `current_email.sender` | string | Who sent it |
| `current_email.subject` | string | Email subject line |
| `current_email.body` | string | Full email body |
| `current_email.has_attachment` | bool | Whether there's an attachment |
| `inbox_count` | int | Emails remaining |
| `processed_count` | int | Emails done so far |
| `current_score` | float 0–1 | Running average score |
| `task_name` | string | "easy" / "medium" / "hard" |
| `instructions` | string | Plain English task instructions |

---

## 🕹️ Action Space

What the agent **can do**:

| Field | Type | Required | Description |
|---|---|---|---|
| `action_type` | enum | ✅ | `classify` / `respond` / `escalate` / `skip` |
| `category` | enum | for classify | `urgent` / `important` / `normal` / `spam` |
| `priority` | enum | for medium+hard | `high` / `medium` / `low` |
| `response_text` | string | for hard task | The written email reply |
| `reason` | string | ❌ | Optional explanation |

### Example Actions

```python
# Easy task
{"action_type": "classify", "category": "urgent", "reason": "Server is down"}

# Medium task
{"action_type": "classify", "category": "spam", "priority": "low"}

# Hard task
{
  "action_type": "respond",
  "category": "urgent",
  "priority": "high",
  "response_text": "Dear customer, I sincerely apologize for the delay. We are treating this as our top priority and will resolve it within 24 hours. Best regards."
}
```

---

## 🎯 Tasks

### Task 1 – Easy: Classify
- **Objective:** Label each email as `urgent`, `important`, `normal`, or `spam`
- **Emails:** 8 (clear, obvious categories)
- **Passing score:** ≥ 0.70
- **Reward:** 1.0 for correct, 0.5 for near-miss, 0.0 for wrong

### Task 2 – Medium: Classify + Prioritize
- **Objective:** Correctly classify AND set priority (`high`/`medium`/`low`)
- **Emails:** 8 (more nuanced, requires judgment)
- **Passing score:** ≥ 0.55
- **Reward:** 50% classification + 50% priority

### Task 3 – Hard: Classify + Prioritize + Respond
- **Objective:** Full email handling with written replies
- **Emails:** 6 (complex real-world situations — angry customers, legal deadlines, PR crises)
- **Passing score:** ≥ 0.40
- **Reward:** 30% classification + 30% priority + 40% response quality

---

## 🏆 Reward Function

Rewards are given **at every step** (not just end of episode):

```
Easy:   reward = classification_score - penalty
Medium: reward = 0.5 × classification + 0.5 × priority - penalty
Hard:   reward = 0.3 × classification + 0.3 × priority + 0.4 × response - penalty
```

**Partial credit is always given:**
- Classifying `urgent` as `important` → 0.5 (near miss)
- Classifying `urgent` as `spam` → 0.0 (completely wrong)
- `skip` action → -0.3 penalty
- Missing response on hard task → -0.3 penalty

---

## 📊 Baseline Scores

| Agent | Easy | Medium | Hard |
|---|---|---|---|
| Random agent | ~0.25 | ~0.17 | ~0.12 |
| GPT-4o-mini (temp=0) | ~0.85 | ~0.72 | ~0.55 |

---

## 🚀 Setup & Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the environment in Python

```python
from env.environment import EmailTriageEnv

env = EmailTriageEnv(task="easy")  # or "medium" or "hard"
obs = env.reset()

while True:
    # Your agent decides an action
    action = {"action_type": "classify", "category": "urgent"}
    
    obs, reward, done, info = env.step(action)
    print(f"Reward: {reward:.3f} | Done: {done}")
    
    if done:
        break

print(f"Final score: {obs['current_score']:.3f}")
```

### 3. Run the tests

```bash
python tests/test_env.py
```

### 4. Run the baseline (needs OpenAI key)

```bash
export OPENAI_API_KEY="sk-..."
python scripts/baseline.py
```

### 5. Start the API server

```bash
python app.py
# → http://localhost:7860
# → http://localhost:7860/docs  (interactive API)
```

---

## 🐳 Docker

```bash
# Build
docker build -t email-triage-openenv .

# Run
docker run -p 7860:7860 -e OPENAI_API_KEY="sk-..." email-triage-openenv
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Homepage |
| GET | `/tasks` | List all tasks |
| POST | `/reset` | Start new episode |
| POST | `/step` | Take an action |
| GET | `/state` | Get current state |
| GET | `/health` | Health check |

### Quick API example

```bash
# Start episode
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "easy"}'

# Take action
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"task": "easy", "action": {"action_type": "classify", "category": "urgent"}}'
```

---

## 🤗 Hugging Face Spaces

This environment is deployed at:  
**`https://huggingface.co/spaces/YOUR_USERNAME/email-triage-openenv`**

Tagged with: `openenv`

---

## 📋 OpenEnv Compliance

| Requirement | Status |
|---|---|
| Typed Observation model | ✅ `env/models.py` |
| Typed Action model | ✅ `env/models.py` |
| Typed Reward model | ✅ `env/models.py` |
| `reset()` method | ✅ `env/environment.py` |
| `step()` method | ✅ `env/environment.py` |
| `state()` method | ✅ `env/environment.py` |
| `openenv.yaml` metadata | ✅ `openenv.yaml` |
| 3 tasks (easy→hard) | ✅ |
| Partial reward signals | ✅ |
| Agent graders 0.0–1.0 | ✅ `graders/graders.py` |
| Baseline inference script | ✅ `scripts/baseline.py` |
| Dockerfile | ✅ |
| HF Spaces deployment | ✅ |

---

## 📄 License

MIT
