"""
Sample emails used in all 3 tasks.
Easy task uses TASK_1_EMAILS, Medium uses TASK_2_EMAILS, Hard uses TASK_3_EMAILS.
"""

from env.models import Email, EmailCategory, EmailPriority

# ──────────────────────────────────────────────
# TASK 1 – EASY: Just CLASSIFY emails
# Clear, obvious emails. Agent must label them correctly.
# ──────────────────────────────────────────────

TASK_1_EMAILS = [
    Email(
        email_id="E001",
        sender="boss@company.com",
        subject="URGENT: Server is down!",
        body="Our production server crashed 10 minutes ago. Customers cannot access the website. Please fix IMMEDIATELY.",
        received_at="2024-01-15 09:00",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
    ),
    Email(
        email_id="E002",
        sender="newsletter@deals.com",
        subject="🎉 50% OFF Everything Today Only!!!",
        body="Click here to get amazing deals! Buy now! Limited time offer! Unsubscribe below.",
        received_at="2024-01-15 09:05",
        true_category=EmailCategory.SPAM,
        true_priority=EmailPriority.LOW,
    ),
    Email(
        email_id="E003",
        sender="hr@company.com",
        subject="Reminder: Submit your timesheet by Friday",
        body="Hi team, just a friendly reminder to submit your timesheets before end of day Friday. Thanks!",
        received_at="2024-01-15 09:10",
        true_category=EmailCategory.NORMAL,
        true_priority=EmailPriority.LOW,
    ),
    Email(
        email_id="E004",
        sender="client@bigcorp.com",
        subject="Contract renewal discussion",
        body="Hi, our contract expires next month. We'd like to schedule a meeting to discuss renewal terms. Please let me know your availability.",
        received_at="2024-01-15 09:15",
        true_category=EmailCategory.IMPORTANT,
        true_priority=EmailPriority.MEDIUM,
    ),
    Email(
        email_id="E005",
        sender="security@company.com",
        subject="URGENT: Suspicious login detected on your account",
        body="We detected a login attempt from an unknown location. If this wasn't you, please reset your password immediately.",
        received_at="2024-01-15 09:20",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
    ),
    Email(
        email_id="E006",
        sender="promo@randomstore.com",
        subject="You won a FREE iPhone!!!",
        body="Congratulations! You have been selected. Click the link to claim your prize now!",
        received_at="2024-01-15 09:25",
        true_category=EmailCategory.SPAM,
        true_priority=EmailPriority.LOW,
    ),
    Email(
        email_id="E007",
        sender="teammate@company.com",
        subject="Quarterly report draft",
        body="Hey, I've attached the draft of our Q4 report. Can you review it before the board meeting next week? No rush, just whenever you get a chance.",
        received_at="2024-01-15 09:30",
        has_attachment=True,
        true_category=EmailCategory.IMPORTANT,
        true_priority=EmailPriority.MEDIUM,
    ),
    Email(
        email_id="E008",
        sender="noreply@system.com",
        subject="Your monthly invoice is ready",
        body="Your invoice #INV-2024-001 for $500 is ready. You can view it in your account dashboard.",
        received_at="2024-01-15 09:35",
        true_category=EmailCategory.NORMAL,
        true_priority=EmailPriority.LOW,
    ),
]


# ──────────────────────────────────────────────
# TASK 2 – MEDIUM: CLASSIFY + PRIORITIZE emails
# More nuanced emails. Agent must do both correctly.
# ──────────────────────────────────────────────

TASK_2_EMAILS = [
    Email(
        email_id="M001",
        sender="vip.client@enterprise.com",
        subject="Issue with our recent order",
        body="We placed an order last week (Order #ORD-5521) and it still hasn't arrived. This is causing significant delays in our production line. We need this resolved today.",
        received_at="2024-01-15 08:00",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="empathetic",
    ),
    Email(
        email_id="M002",
        sender="intern@company.com",
        subject="Question about PTO policy",
        body="Hi, I wanted to ask about the paid time off policy. How many days do interns get? I was planning a short trip next month.",
        received_at="2024-01-15 08:10",
        true_category=EmailCategory.NORMAL,
        true_priority=EmailPriority.LOW,
        expected_response_tone="friendly",
    ),
    Email(
        email_id="M003",
        sender="legal@lawfirm.com",
        subject="Compliance deadline – action required by Jan 20",
        body="Dear team, per our previous correspondence, you must submit the compliance documentation by January 20th or face penalties. Please confirm receipt.",
        received_at="2024-01-15 08:20",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="professional",
    ),
    Email(
        email_id="M004",
        sender="partner@startup.com",
        subject="Potential collaboration opportunity",
        body="Hello! We are a startup working on AI tools and think there could be a great synergy between our companies. Would love to set up a quick call sometime this month.",
        received_at="2024-01-15 08:30",
        true_category=EmailCategory.IMPORTANT,
        true_priority=EmailPriority.MEDIUM,
        expected_response_tone="professional",
    ),
    Email(
        email_id="M005",
        sender="alerts@monitoring.com",
        subject="Warning: CPU usage at 95% on prod-server-02",
        body="Automated alert: prod-server-02 has been running at 95% CPU for the last 15 minutes. Manual intervention may be required.",
        received_at="2024-01-15 08:40",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="brief",
    ),
    Email(
        email_id="M006",
        sender="events@techconf.com",
        subject="You are invited: Tech Summit 2024",
        body="We'd like to invite you to speak at Tech Summit 2024 in March. It's a great opportunity to share your expertise with 2000+ attendees.",
        received_at="2024-01-15 08:50",
        true_category=EmailCategory.IMPORTANT,
        true_priority=EmailPriority.MEDIUM,
        expected_response_tone="professional",
    ),
    Email(
        email_id="M007",
        sender="accounts@vendor.com",
        subject="Overdue payment notice – Invoice #7821",
        body="This is a reminder that Invoice #7821 for $12,400 was due on January 1st and remains unpaid. Please process payment immediately to avoid service interruption.",
        received_at="2024-01-15 09:00",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="professional",
    ),
    Email(
        email_id="M008",
        sender="team@company.com",
        subject="Office snacks poll 🍕",
        body="Hey everyone! We're restocking the kitchen. Vote for your favorite snacks using the link below. Poll closes Friday!",
        received_at="2024-01-15 09:10",
        true_category=EmailCategory.NORMAL,
        true_priority=EmailPriority.LOW,
        expected_response_tone="friendly",
    ),
]


# ──────────────────────────────────────────────
# TASK 3 – HARD: CLASSIFY + PRIORITIZE + RESPOND
# Agent must write good replies. Graded on tone + content.
# ──────────────────────────────────────────────

TASK_3_EMAILS = [
    Email(
        email_id="H001",
        sender="angry.customer@email.com",
        subject="WORST SERVICE EVER – I want a refund NOW",
        body="I have been waiting 3 weeks for my order and nobody is helping me. I have called 5 times. This is completely unacceptable. I want a full refund immediately or I will dispute with my bank.",
        received_at="2024-01-15 07:00",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="empathetic",
    ),
    Email(
        email_id="H002",
        sender="ceo@bigclient.com",
        subject="Considering ending our partnership",
        body="We've been partners for 5 years but recent service quality has declined significantly. Unless we see major improvements in the next 30 days, we will be moving to a competitor. I'd like to discuss this on a call.",
        received_at="2024-01-15 07:30",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="empathetic",
    ),
    Email(
        email_id="H003",
        sender="journalist@techblog.com",
        subject="Request for comment on data breach rumors",
        body="Hi, I'm writing an article about reports of a data breach at your company last week. I'd like to give you the opportunity to comment before we publish tomorrow morning.",
        received_at="2024-01-15 08:00",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="professional",
    ),
    Email(
        email_id="H004",
        sender="new.employee@company.com",
        subject="I think I made a mistake on my first day",
        body="Hi, I accidentally sent an internal spreadsheet to the wrong email address. I'm not sure what to do. I'm really worried. The file had some customer data in it.",
        received_at="2024-01-15 08:30",
        true_category=EmailCategory.URGENT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="empathetic",
    ),
    Email(
        email_id="H005",
        sender="investor@vcfund.com",
        subject="Follow up from our meeting",
        body="Great meeting you last week. We are seriously considering the investment. Could you send over the updated financial projections and cap table before our committee meeting on Friday?",
        received_at="2024-01-15 09:00",
        true_category=EmailCategory.IMPORTANT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="professional",
    ),
    Email(
        email_id="H006",
        sender="employee@company.com",
        subject="Feeling overwhelmed and need to talk",
        body="I wanted to reach out because I've been really struggling with my workload lately. I don't want to let the team down but I'm not sure how much longer I can keep up this pace.",
        received_at="2024-01-15 09:30",
        true_category=EmailCategory.IMPORTANT,
        true_priority=EmailPriority.HIGH,
        expected_response_tone="empathetic",
    ),
]
