"""Output formatters for CLI."""

from ..ai import (
    create_client,
    daily_review_prompt,
    monthly_analysis_prompt,
    weekly_analysis_prompt,
)
from ..services import TrackerService
from ..services.report_service import _collect_month, _collect_week
from ..utils import CYAN, RESET, fmt_bold, heading, info


def format_review(service: TrackerService, stream: bool = True) -> None:
    """Format and print daily review."""
    from ..models import parse_entries

    data = parse_entries()
    if not data["activities"]:
        from ..utils import err
        err("No activities logged today. Log something first!")
        return

    heading("🧠 AI Daily Review")

    ai = service.ai
    if not ai:
        from ..utils import err
        err("No API key configured. Run 'tracker init' and set your key.")
        return

    prompt = daily_review_prompt()
    resp = ai.ask(
        prompt,
        system_prompt="You are a brutally honest, time-aware life coach. ALWAYS compare the user's logs, goals and progress against the CURRENT TIME provided in the prompt. Do NOT treat every review as end-of-day — if it's morning, give a check-in; if midday, give a mid-day correction; only at night give a final roast. Also consider sleep patterns and day context.",
        stream=stream,
    )
    if stream:
        if resp is None:
            from ..utils import err
            err("Empty response from AI.")
        else:
            print(f"{CYAN}{'─' * 50}{RESET}")
    elif resp:
        print(f"{CYAN}{'─' * 50}{RESET}")
        info(fmt_bold(resp))
        print(f"{CYAN}{'─' * 50}{RESET}")


def format_weekly(service: TrackerService, stream: bool = True) -> None:
    heading("📊 Generating weekly report...")
    from ..services import weekly
    report = weekly()
    print(report)

    if service.ai:
        from ..services import _collect_week
        data = _collect_week()
        prompt = weekly_analysis_prompt(data)
        heading("🤖 AI Weekly Analysis")
        resp = service.ai.ask(
            prompt,
            system_prompt="You are a brutally honest productivity coach.",
            stream=stream,
        )
        if stream:
            if resp is None:
                from ..utils import err
                err("Empty response from AI.")
        elif resp:
            info(fmt_bold(resp))


def format_monthly(service: TrackerService, stream: bool = True) -> None:
    heading("📊 Generating monthly report...")
    from ..services import monthly
    report = monthly()
    print(report)

    if service.ai:
        from ..services import _collect_month
        data = _collect_month()
        prompt = monthly_analysis_prompt(data)
        heading("🤖 AI Monthly Analysis")
        resp = service.ai.ask(
            prompt,
            system_prompt="You are a brutally honest life coach.",
            stream=stream,
        )
        if stream:
            if resp is None:
                from ..utils import err
                err("Empty response from AI.")
        elif resp:
            info(fmt_bold(resp))