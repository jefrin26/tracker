"""Prompt templates for AI reviews."""

from ..models import parse_entries
from ..models.sleep import get_today as get_sleep
from ..models.day_context import get_context


def daily_review_prompt() -> str:
    """Build the daily review prompt with full context."""
    data = parse_entries()

    activities_str = "\n".join(
        f"  {a['time']} | {a['activity']} ({a['duration']}) — {a['type']}"
        for a in data["activities"]
    )
    goals_str = ", ".join(data["goals"]) or "None"
    completed_str = ", ".join(data["completed"]) or "None"
    scores = data["scores"]

    sleep_data = get_sleep()
    if sleep_data["uptime"]:
        sleep_info = f"{sleep_data['uptime']} (bedtime: {sleep_data['bedtime']}, wake: {sleep_data['wake_time']})"
    else:
        sleep_info = "No data recorded"

    day_data = get_context()
    if day_data["day_type"] != "normal":
        day_info = f"{day_data['day_type']} — {day_data['notes']}"
    else:
        day_info = "normal"

    return (
        f"You are my brutally honest life coach who knows my sleep and day context.\n\n"
        f"Here's my log for today:\n\n"
        f"Activities:\n{activities_str}\n\n"
        f"Goals: {goals_str}\n"
        f"Completed: {completed_str}\n\n"
        f"Scores: Productivity: {scores['productivity']}/10, Energy: {scores['energy']}/10, Mood: {scores['mood']}/10\n\n"
        f"🌙 Sleep: {sleep_info}\n"
        f"📅 Day: {day_info}\n\n"
        f"Answer these:\n"
        "1. Rate my day out of 10 (be harsh, no participation trophies)\n"
        "2. What was my biggest time sink?\n"
        "3. What should I have done differently?\n"
        "4. One thing to carry forward to tomorrow\n"
        "5. Call out any BS or excuses you see\n\n"
        "Keep it under 150 words. Make it hit hard."
    )


def weekly_analysis_prompt(week_data: str) -> str:
    return (
        f"Here's my week:\n\n{week_data}\n\n"
        "Analyze:\n"
        "1. Productivity trend (up/down/flat)\n"
        "2. Most wasted time category\n"
        "3. Most productive time of day\n"
        "4. One hard truth I need to hear\n"
        "5. Goal for next week (specific, measurable)\n\n"
        "Be ruthless. I need the truth, not comfort."
    )


def monthly_analysis_prompt(month_data: str) -> str:
    return (
        f"Here's my month:\n\n{month_data[:4000]}\n\n"
        "Give me:\n"
        "1. Overall productivity score /10\n"
        "2. Top 3 accomplishments\n"
        "3. Biggest time waster\n"
        "4. Trend vs last month\n"
        "5. One thing to change next month\n"
        "Keep it concise and honest."
    )