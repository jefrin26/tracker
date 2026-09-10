"""Goal management service."""

from datetime import datetime
from ..models import add_goal, done_goal


def add(goal_text: str, date: datetime | None = None) -> str:
    return add_goal(goal_text, date)


def complete(goal_text: str, date: datetime | None = None) -> str:
    return done_goal(goal_text, date)