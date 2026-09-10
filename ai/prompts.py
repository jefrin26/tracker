"""Prompt templates for AI reviews."""

from ..models import parse_entries
from ..models.sleep import get_today as get_sleep
from ..models.day_context import get_context


def daily_review_prompt(now=None) -> str:
    """Build the daily review prompt with full context — time-aware.

    Compares logged time, goals and current time so the AI does NOT
    always act like it's end-of-day. `now` is injectable for tests.
    """
    from datetime import datetime as _dt
    from ..config import get_config
    from ..utils.time_utils import day_progress_info, parse_time, to_minutes, duration_between

    n = now or _dt.now()
    now_str = n.strftime("%H:%M")
    date_str = n.strftime("%Y-%m-%d")
    weekday = n.strftime("%A")

    # Config / wake-sleep window
    try:
        cfg = get_config()
    except Exception:
        cfg = {}
    wake_str = cfg.get("wake_time") or cfg.get("wake_time") or "07:00"
    # config uses sleep_time/wake_time, but sleep module uses bedtime
    wake_str = cfg.get("wake_time", "07:00")
    sleep_str = cfg.get("sleep_time", "23:00")
    target_h = float(cfg.get("daily_target_hours", 4))

    prog = day_progress_info(n, wake_str=wake_str, sleep_str=sleep_str)
    phase = prog["phase"]
    elapsed_wake_h = prog["elapsed_wake_h"]
    remaining_wake_h = prog["remaining_wake_h"]
    pct_wake = prog["pct_wake"]
    pct_mid = prog["pct_mid"]

    data = parse_entries()

    def _fmt_activity(a: dict) -> str:
        if a.get("end"):
            time_part = f"{a['start']} → {a['end']}"
        else:
            time_part = a.get("time", a.get("start", ""))
        return f"  {time_part} | {a['activity']} ({a['duration']}) — {a['type']}"

    activities_str = "\n".join(_fmt_activity(a) for a in data["activities"]) or "  (none yet)"

    # Total logged minutes — time-aware: only count logs that have started at/before now
    total_m_all = 0
    total_m_so_far = 0
    future_m = 0
    for a in data["activities"]:
        d = a.get("duration", "").replace("m", "").strip()
        if not d.isdigit():
            continue
        dur = int(d)
        total_m_all += dur
        s = a.get("start", "")
        s_m = to_minutes(*parse_time(s)) if s and parse_time(s) else None  # type: ignore
        cur_m_tmp = to_minutes(n.hour, n.minute)
        # If start is in future relative to now, it's future scheduled
        if s_m is not None and s_m > cur_m_tmp:
            # Check overnight case: if start 23:00 and now 01:00 next day, start > cur but it's not future — it's yesterday
            # For simplicity, if gap is large and activity is overnight, treat as not future
            # We'll consider future only if start is within same day and ahead
            future_m += dur
        else:
            total_m_so_far += dur
    # Use so_far for progress, but also show all for context
    total_m = total_m_so_far
    total_h = total_m / 60
    total_all_h = total_m_all / 60
    pct_target = (total_h / target_h * 100) if target_h else 0
    pct_target_all = (total_all_h / target_h * 100) if target_h else 0

    # Find most recent end time and gaps — time-aware
    last_end = None
    first_start = None
    gap_str = "unknown"
    ongoing_info = ""
    if data["activities"]:
        # Activities are newest-first (insertion after separator), but sort not needed for first/last
        # first_start = oldest
        first_start = data["activities"][-1].get("start") or data["activities"][-1].get("time", "").split("→")[0].strip()
        # For gap, find the most relevant activity relative to now
        cur_m = to_minutes(n.hour, n.minute)
        # Parse all activities with start/end
        parsed = []
        for a in data["activities"]:
            s = a.get("start") or ""
            e = a.get("end") or ""
            s_m = to_minutes(*parse_time(s)) if s and parse_time(s) else None  # type: ignore
            e_m = to_minutes(*parse_time(e)) if e and parse_time(e) else s_m
            parsed.append((a, s_m, e_m))
        # Check for ongoing activity: start <= now <= end
        ongoing = None
        for a, s_m, e_m in parsed:
            if s_m is not None and e_m is not None:
                # Handle overnight: if end < start, end is next day
                s, e = s_m, e_m
                cur = cur_m
                # If activity is overnight (e < s), adjust
                if e is not None and s is not None and e < s:
                    e += 24 * 60
                    if cur < s:
                        cur += 24 * 60
                if s <= cur <= e:
                    ongoing = (a, s, e, cur)
                    break
        if ongoing:
            a, s, e, cur = ongoing
            remaining = e - cur
            gap_str = f"currently ACTIVE in '{a['activity']}' ({a['start']} → {a['end']}, {remaining}m remaining)"
            last_end = a.get("end") or a.get("start")
        else:
            # Find last completed before now
            last_completed = None
            last_m = -1
            for a, s_m, e_m in parsed:
                if e_m is not None and e_m <= cur_m and e_m > last_m:
                    last_m = e_m
                    last_completed = a
            if last_completed:
                last_end = last_completed.get("end") or last_completed.get("start")
                assert last_end is not None
                gap_m = cur_m - last_m
                if gap_m == 0:
                    gap_str = "just now"
                elif gap_m < 60:
                    gap_str = f"{gap_m}m ago (last ended at {last_end}, now {now_str})"
                else:
                    gap_str = f"{gap_m // 60}h {gap_m % 60}m ago (last ended at {last_end}, now {now_str})"
            else:
                # No completed yet — find next upcoming
                next_start = None
                next_m = 24 * 60 + 1
                next_a = None
                for a, s_m, e_m in parsed:
                    if s_m is not None and s_m > cur_m and s_m < next_m:
                        next_m = s_m
                        next_a = a
                if next_a:
                    wait = next_m - cur_m
                    last_end = next_a.get("end") or next_a.get("start")
                    if wait < 60:
                        gap_str = f"no completed logs yet before {now_str} — next starts at {next_a['start']} in {wait}m"
                    else:
                        gap_str = f"no completed logs yet before {now_str} — next starts at {next_a['start']} in {wait // 60}h {wait % 60}m"
                    # For first_start/last_end display, keep next's start as last_end for info
                    last_end = next_a.get("end") or next_a.get("start")
                else:
                    # Fallback to most recent overall
                    last_end = data["activities"][0].get("end") or data["activities"][0].get("start")
                    gap_str = f"last log {last_end} (all logs are in future relative to {now_str})"
        # If not ongoing, ensure last_end is set for display
        if not last_end:
            last_end = data["activities"][0].get("end") or data["activities"][0].get("start")

    # Coverage vs elapsed
    elapsed_mid_h = prog["elapsed_mid_h"]
    # Unlogged since wake
    unlogged_wake_h = max(0, elapsed_wake_h - total_h)
    # Unlogged since midnight
    unlogged_mid_h = max(0, elapsed_mid_h - total_h)

    goals = [g for g in data["goals"] if g.strip()]
    completed = [c for c in data["completed"] if c.strip()]
    pending = [g for g in goals if g not in completed]
    goals_str = ", ".join(goals) or "None"
    completed_str = ", ".join(completed) or "None"
    pending_str = ", ".join(pending) or "None"
    goals_total = len(goals)
    goals_done = len(completed)
    goals_pct = (goals_done / goals_total * 100) if goals_total else 0

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

    # Determine review mode based on time
    if pct_wake < 30 or n.hour < 12:
        mode_hint = "MORNING / EARLY — Day is still young. This is a check-in, NOT an end-of-day roast. Focus on momentum, what's working, what to prioritize NEXT in the remaining hours. Do NOT give a final day rating as if day is over; give a 'so far' assessment and what to fix before evening."
        rating_q = "1. Rate my progress so far out of 10 (not final day, just progress vs time elapsed)"
        carry_q = "4. One thing to nail in the NEXT 3 hours (specific, actionable)"
    elif pct_wake < 70 or 12 <= n.hour < 18:
        mode_hint = "MIDDAY / AFTERNOON — Mid-day review. Compare logged time vs time elapsed, call out pace vs target, identify biggest time sink SO FAR, and what to adjust in the remaining hours."
        rating_q = "1. Rate my pace so far out of 10 (are you on track vs time?)"
        carry_q = "4. One thing to fix in the remaining hours today"
    else:
        mode_hint = "EVENING / NIGHT — End-of-day review. Day is mostly done. Give a final harsh rating, biggest time sink, what to do differently, and one thing to carry to tomorrow."
        rating_q = "1. Rate my day out of 10 (final, be harsh)"
        carry_q = "4. One thing to carry forward to tomorrow"

    # If very late at night after sleep time, note it
    late_note = ""
    if n.hour >= 23 or n.hour < 5:
        late_note = " Note: It's late at night — consider whether remaining tasks should be deferred to tomorrow."

    return (
        f"You are my brutally honest, time-aware life coach who knows my sleep and day context.\n"
        f"CRITICAL: Adapt your tone to the CURRENT TIME. Do NOT always act like it's end-of-day. Compare logs/goals against time elapsed and remaining.\n\n"
        f"CURRENT TIME: {date_str} {now_str} ({weekday}) — Phase: {phase.upper()} — {pct_wake:.0f}% through waking day (wake {wake_str} → sleep {sleep_str})\n"
        f"  • Elapsed since wake: {elapsed_wake_h:.1f}h | Remaining until sleep: {remaining_wake_h:.1f}h | Midnight progress: {pct_mid:.0f}% ({elapsed_mid_h:.1f}h elapsed, {24 - elapsed_mid_h:.1f}h left)\n"
        f"  • Mode: {mode_hint}{late_note}\n\n"
        f"Today's log SO FAR (up to {now_str}):\n"
        f"Activities (all logged today — future entries are marked):\n{activities_str}\n"
        f"  • First log started at: {first_start or '—'} | Last log ended at: {last_end or '—'} | Gap since last log: {gap_str}\n"
        f"  • Total logged SO FAR (up to {now_str}): {total_h:.1f}h / target {target_h:.1f}h ({pct_target:.0f}%)"
        + (f" | Plus future scheduled: {future_m/60:.1f}h (total all {total_all_h:.1f}h, {pct_target_all:.0f}% of target)" if future_m else "")
        + "\n"
        f"  • Coverage vs elapsed (wake): {total_h:.1f}h logged so far of {elapsed_wake_h:.1f}h elapsed → unlogged/idle ~{unlogged_wake_h:.1f}h\n"
        f"  • Coverage vs midnight: {total_h:.1f}h logged so far of {elapsed_mid_h:.1f}h elapsed → unlogged ~{unlogged_mid_h:.1f}h\n\n"
        f"Goals: {goals_str} ({goals_total} total, {goals_done} done, {goals_pct:.0f}%)\n"
        f"Completed: {completed_str}\n"
        f"Pending: {pending_str}\n\n"
        f"Scores: Productivity: {data['scores']['productivity']}/10, Energy: {data['scores']['energy']}/10, Mood: {data['scores']['mood']}/10\n\n"
        f"🌙 Sleep: {sleep_info}\n"
        f"📅 Day: {day_info}\n\n"
        f"Answer these (keep under 150 words, harsh, time-aware):\n"
        f"{rating_q}\n"
        "2. What was my biggest time sink SO FAR (or up to now)?\n"
        "3. What should I have done differently given the time?\n"
        f"{carry_q}\n"
        "5. Call out any BS or excuses you see — considering current time (don't invent end-of-day failures if it's still morning)\n\n"
        "Make it hit hard and be useful RIGHT NOW, not generic end-of-day advice."
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