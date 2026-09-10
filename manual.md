# Tracker — User Manual

> **Personal AI Tracking Assistant — powered by OpenRouter**
> Version `2.0.0` · Python ≥ 3.10 · Entry point `tracker.main:main` (`tracker/__main__.py:1`)

---

## Table of Contents

1. [What Is Tracker?](#1-what-is-tracker)
2. [Requirements](#2-requirements)
3. [Installation](#3-installation)
4. [Quick Start](#4-quick-start)
5. [Where Your Data Lives](#5-where-your-data-lives)
6. [Configuration (`~/tracker/config.json`)](#6-configuration-trackerconfigjson)
7. [The Daily Log Format](#7-the-daily-log-format)
8. [Command Reference](#8-command-reference)
   - [8.1 `tracker init`](#81-tracker-init)
   - [8.2 `tracker log`](#82-tracker-log)
   - [8.3 `tracker goal` / `tracker done`](#83-tracker-goal--tracker-done)
   - [8.4 `tracker today` / `tracker yesterday`](#84-tracker-today--tracker-yesterday)
   - [8.5 `tracker sleep`](#85-tracker-sleep)
   - [8.6 `tracker special`](#86-tracker-special)
   - [8.7 `tracker habit`](#87-tracker-habit)
   - [8.8 `tracker project`](#88-tracker-project)
   - [8.9 `tracker stats` / `tracker report`](#89-tracker-stats--tracker-report)
   - [8.10 `tracker review`](#810-tracker-review)
   - [8.11 `tracker week` / `tracker month`](#811-tracker-week--tracker-month)
   - [8.12 `tracker search`](#812-tracker-search)
   - [8.13 `tracker export`](#813-tracker-export)
9. [AI Features](#9-ai-features)
10. [Typical Workflows](#10-typical-workflows)
11. [Tips & Reference](#11-tips--reference)
12. [Troubleshooting & FAQ](#12-troubleshooting--faq)

---

## 1. What Is Tracker?

Tracker is a **local-first, markdown-backed, CLI time-tracker** with AI review capabilities. Every activity, goal, habit, sleep record, and day-context note is written to plain files under `~/tracker/` (`tracker/storage/file_storage.py:11`), so your data is always portable. An optional OpenRouter API key unlocks brutally-honest daily/weekly/monthly coaching via `tracker review` / `week` / `month` (`tracker/ai/client.py:12`, `tracker/ai/prompts.py:8`).

Core ideas:

- **One markdown file per day** — `~/tracker/daily/YYYY/MM/YYYY-MM-DD.md` generated from a template (`tracker/models/daily_log.py:14`).
- **Append-only logging** — `tracker log` inserts a row right after the table separator (`tracker/models/daily_log.py:97`).
- **Streak-aware habits** — streak increments only when yesterday was the last done date (`tracker/models/habit.py:52`).
- **Overnight-aware sleep** — wake ≤ bedtime is treated as next-day uptime (`tracker/utils/time_utils.py:42`).
- **Explicit commands, interactive fallback** — omit arguments and Tracker prompts you (`tracker/cli/commands.py:40`, `tracker/services/log_service.py:20`).

---

## 2. Requirements

| Requirement | Notes |
|---|---|
| Python | ≥ 3.10 (`pyproject.toml:9`) |
| Network | Only needed for AI commands (`review`, `week`, `month`); everything else works offline |
| OpenRouter API key | Optional; obtain at https://openrouter.ai — set during `tracker init` or in `~/tracker/config.json` |
| Dependencies | `requests` for the AI client (`tracker/ai/client.py:7`) — install via `pip` if not already present |

---

## 3. Installation

From the project root (`/home/jefrin/code/python/`):

```bash
# 1. Clone / enter the repo
cd /home/jefrin/code/python

# 2. Install in editable mode (exposes the `tracker` console script)
pip install -e .

# 3. Verify
tracker --help
python -m tracker --help   # equivalent via tracker/__main__.py:1
```

If you prefer not to install the script:

```bash
python -m tracker init
python -m tracker log "Deep work" 60 work
```

> The console script is defined at `pyproject.toml:13` as `tracker = "tracker.main:main"`.

---

## 4. Quick Start

```bash
# Initialize folders + config + today's log
tracker init
# → prompts: "Enter your OpenRouter API key (or leave blank)"

# Log work
tracker log "Study networking" 30 work
tracker log "Built subnet calculator" 90 study --notes "CIDR /24"

# Or use interactive mode (omit args)
tracker log
# Activity: Study networking
# Duration (minutes): 30
# Type (work/study/...): work
# Notes (optional):

# Set goals and close them
tracker goal "Learn subnetting"
tracker done "Learn subnetting"

# Track sleep and context
tracker sleep --bedtime 23:00 --wakeup 07:00
tracker special exam --notes "Finals week"

# Build a habit streak
tracker habit "Morning run"
tracker habit --show

# See today / yesterday
tracker today
tracker yesterday

# Stats and AI coaching
tracker stats
tracker report
tracker review              # streams by default
tracker week --no-stream    # disable streaming
tracker month

# Search & export
tracker search networking
tracker export json
```

---

## 5. Where Your Data Lives

All data lives under `TRACKER_HOME = ~/tracker` (`tracker/config.py:7`). Created on `tracker init` (`tracker/services/tracker_service.py:37`):

```
~/tracker/
├── config.json                 # settings + API key (tracker/config.py:23)
├── daily/
│   └── YYYY/MM/YYYY-MM-DD.md   # one file per day (tracker/storage/file_storage.py:11)
├── weekly/
│   └── YYYY-Www.md             # generated by `tracker week` (tracker/storage/file_storage.py:34)
├── monthly/
│   └── YYYY-MM.md              # generated by `tracker month` (tracker/storage/file_storage.py:44)
├── projects/
│   └── <name>/
│       ├── progress.md
│       ├── milestones.md
│       └── notes.md            # created by `tracker project` (tracker/models/project.py:13)
├── habits/
│   └── habits.md               # habit table (tracker/storage/file_storage.py:19)
├── day_context/
│   └── YYYY-MM-DD.json         # exam/college/holiday/normal (tracker/storage/file_storage.py:25)
└── export/
    └── YYYY-MM-DD.json         # JSON export (tracker/storage/file_storage.py:60)
```

Every file is plain text — you can open, edit, back up, or version-control `~/tracker` with any tool.

---

## 6. Configuration (`~/tracker/config.json`)

Created from `DEFAULT_CONFIG` (`tracker/config.py:9`). Edit directly or re-run `tracker init`.

```json
{
  "api_key": "",
  "daily_target_hours": 4,
  "sleep_time": "23:00",
  "wake_time": "07:00",
  "habit_streak_reset_hours": 24,
  "review_time": "21:00",
  "name": "Your Name",
  "special_day": {},
  "bedtime": null,
  "wakeup": null,
  "model": "openrouter/free"
}
```

| Key | Purpose | Used By |
|---|---|---|
| `api_key` | OpenRouter bearer token | `tracker/ai/client.py:18`, `tracker/services/tracker_service.py:19` |
| `model` | OpenRouter model id (default `openrouter/free`) | `tracker/ai/client.py:17` |
| `daily_target_hours` | Target for progress bar | `tracker/services/stats_service.py:29` |
| `sleep_time` / `wake_time` | Default hints for sleep display | Config only (not auto-applied) |
| `habit_streak_reset_hours` | Reserved for future streak window logic | Config only |
| `review_time` | Reserved / informational | Config only |
| `name` | Display name | Config only |

If `config.json` is missing, any command that calls `load_config()` (`tracker/config.py:26`) will error with `Run 'tracker init' first.`

> **Security:** `config.json` contains your API key in plain text. Keep `~/tracker/` permissions restricted (`chmod 700 ~/tracker`).

---

## 7. The Daily Log Format

Each day's file is initialized from `template()` (`tracker/models/daily_log.py:14`):

```markdown
# Daily Log — 2026-09-10

## 🎯 Goals
- [ ] 

## ⏰ Time Log
| Time | Activity | Duration | Type | Notes |
|------|----------|----------|------|-------|
| 09:15 | Study networking | 30m | work | CIDR notes |

## 🌙 Sleep
| Bedtime | Wake Time | Uptime | Notes |
|---------|-----------|--------|-------|
| 23:00 | 07:00 | 8.0h |  |

## 📅 Day Context
- Type: _normal_ (exam / college / holiday / normal)
- Notes: 

## ✅ Accomplished
## 💡 Learnings
## 🏆 Wins
## 😤 Struggles
## 📊 Scores
- Productivity: _/10
- Energy: _/10
- Mood: _/10

## 📝 Raw Notes
```

- **Time Log** rows are auto-sorted by insertion order; new rows are inserted immediately after the `|---|---|` separator (`tracker/models/daily_log.py:97`).
- **Sleep** holds a single upserted row; logging bedtime/wakeup rewrites that row and recalculates uptime (`tracker/models/sleep.py:15`).
- **Goals** use markdown checkboxes (`- [ ]` / `- [x]`); `tracker done` flips the first exact match (`tracker/models/daily_log.py:145`).
- **Scores** are `_`/10 placeholders until set programmatically via `set_scores()` (`tracker/models/daily_log.py:152`).

### Activity Types

Allowed `type` values (`tracker/models/daily_log.py:11`):

```
work  study  rest  eat  social  exercise  chores  wasted
```

`wasted` triggers a nudging reaction; durations ≥ 60 min get a fire message (`tracker/models/daily_log.py:116`).

---

## 8. Command Reference

Global help: `tracker --help` / `tracker <command> --help`. Subcommands are registered in `tracker/cli/parser.py:11` and dispatched in `tracker/main.py:29`.

### 8.1 `tracker init`

Initialize directory tree and config.

```bash
tracker init
```

- Creates `daily/ weekly/ monthly/ projects/ habits/ export/ day_context/` under `~/tracker` (`tracker/services/tracker_service.py:37`).
- Writes `DEFAULT_CONFIG` to `config.json` if absent (`tracker/services/tracker_service.py:50`), then prompts for an OpenRouter key.
- Ensures today's log file exists (`tracker/models/daily_log.py:55`).
- Idempotent — re-running prints `Config already exists — skipping.` (`tracker/services/tracker_service.py:60`).

### 8.2 `tracker log`

Log an activity.

```bash
tracker log [activity] [duration] [type] [--notes TEXT | -n TEXT]
```

| Arg | Type | Default | Notes |
|---|---|---|---|
| `activity` | str | — | Description, e.g. `"Study networking"` |
| `duration` | int | — | Minutes |
| `type` | str | `work` | One of `TYPES` |
| `--notes` / `-n` | str | `""` | Free-form note |

- **Direct mode:** all three positionals supplied → immediately appends via `log_activity()` → `add_activity()` (`tracker/cli/commands.py:36`, `tracker/services/log_service.py:7`).
- **Interactive mode:** any positional missing → prompts for activity, duration, type, notes (`tracker/services/log_service.py:20`).
- Time is auto-stamped as `HH:MM` (`tracker/models/daily_log.py:84`).

Examples:

```bash
tracker log "Study networking" 30 work
tracker log "Gym" 45 exercise --notes "leg day"
tracker log "Scrolling reels" 25 wasted
tracker log   # interactive
```

### 8.3 `tracker goal` / `tracker done`

Manage today's checkbox goals (`tracker/models/daily_log.py:123`, `tracker/models/daily_log.py:138`).

```bash
tracker goal "Learn subnetting"
tracker done "Learn subnetting"   # must match exactly
```

- `goal` inserts a new `- [ ] <text>` line under `## 🎯 Goals`.
- `done` replaces the first `- [ ] <text>` with `- [x] <text>`; returns `Goal '...' not found.` if no exact match.

### 8.4 `tracker today` / `tracker yesterday`

Render the raw markdown for today / yesterday.

```bash
tracker today
tracker yesterday
```

Implemented as `display()` / `display(yesterday)` (`tracker/cli/commands.py:53`, `tracker/models/daily_log.py:171`). If the file is empty: `No log for YYYY-MM-DD.`

### 8.5 `tracker sleep`

Log bedtime and/or wake time (`tracker/models/sleep.py:82`, `tracker/models/sleep.py:96`).

```bash
tracker sleep --bedtime 23:00 [--wakeup 07:00] [--notes "..." | -n "..."]
tracker sleep   # interactive
```

- Time format strictly `HH:MM` / `H:MM` validated by `parse_time()` (`tracker/utils/time_utils.py:11`); invalid → `Invalid time format. Use HH:MM (e.g. 23:00).`
- Uptime is computed overnight-aware: wake ≤ bedtime adds 24 h (`tracker/utils/time_utils.py:42`) and formatted as `X.Xh` (`tracker/utils/time_utils.py:46`).
- Bedtime and wakeup can be logged independently; the other field preserves the last stored value (`tracker/models/sleep.py:90`, `tracker/models/sleep.py:104`).
- Both can be supplied together: `tracker sleep --bedtime 23:00 --wakeup 07:00`.

Examples:

```bash
tracker sleep --bedtime 23:30
tracker sleep --wakeup 06:45 --notes "woke early"
tracker sleep --bedtime 00:15 --wakeup 08:00
```

### 8.6 `tracker special`

Set day context — `exam` / `college` / `holiday` / `normal` (`tracker/models/day_context.py:10`).

```bash
tracker special [day_type] [--notes TEXT | -n TEXT]
tracker special          # interactive
```

| Value | Meaning |
|---|---|
| `exam` | Exam / study-intensive day |
| `college` | College / classes day |
| `holiday` | Holiday / off day |
| `normal` | Regular day (default) |

Stored as `~/tracker/day_context/YYYY-MM-DD.json` (`tracker/storage/file_storage.py:25`). Invalid type → `Invalid day type. Use one of: ...` (`tracker/models/day_context.py:17`). The value is surfaced in daily AI prompts (`tracker/ai/prompts.py:26`).

Examples:

```bash
tracker special exam --notes "Final exam — OS"
tracker special holiday --notes "Family trip"
tracker special normal
```

### 8.7 `tracker habit`

Track streaks for any named habit (`tracker/models/habit.py:21`).

```bash
tracker habit [name]
tracker habit --show
```

- `tracker habit "Morning run"` — logs today; creates the habit if new (streak 1), increments if yesterday was last done, resets to 1 otherwise, updates `best` and last-7 history (`tracker/models/habit.py:52`).
- Re-logging the same habit on the same day is a no-op (row unchanged) (`tracker/models/habit.py:48`).
- `tracker habit --show` prints the full markdown table (`tracker/models/habit.py:81`).
- Bare `tracker habit` with no name and no `--show` → `Provide a habit name or use --show` (`tracker/cli/commands.py:85`).

Table shape:

```markdown
| Habit | Streak | Best | Last Done | History (recent 7) |
|-------|--------|------|-----------|--------------------|
| Morning run | 4 | 7 | 2026-09-10 | 2026-09-07, 2026-09-08, 2026-09-09, 2026-09-10 |
```

Streak ≥ 3 appends 🔥 to the success message (`tracker/models/habit.py:77`).

### 8.8 `tracker project`

Open or create a project (`tracker/models/project.py:8`).

```bash
tracker project <name>
```

- Creates `~/tracker/projects/<name>/` with `progress.md`, `milestones.md`, `notes.md` if absent.
- Prints `✅ Created project '<name>' with files.` on first creation.
- Always prints the current `progress.md` content.

Example:

```bash
tracker project tracker-v2
# → edit ~/tracker/projects/tracker-v2/progress.md
```

### 8.9 `tracker stats` / `tracker report`

```bash
tracker stats
tracker report
```

- `stats` (`tracker/services/stats_service.py:68`) prints **today** (hours, entry count, target progress bar) + **week** (total, best day, per-day bar chart). Today parses the Time Log table (`tracker/services/stats_service.py:7`); week aggregates Mon–Sun (`tracker/services/stats_service.py:43`).

  Example output:

  ```
  Today: 2.5h logged (3 entries)
  Target: 4h (62%)
  Progress: [████████████░░░░░░░░]

  Week total: 12.3h
  Best day: Tue (3.2h)

  Daily breakdown:
    Mon   1.5h ██████
    Tue   3.2h ███████████████
    ...
  ```

- `report` (`tracker/services/tracker_service.py:86`) prints `stats` + `today` + `show_habits()` (`tracker/models/habit.py:81`) concatenated with blank lines — a one-page daily dashboard.

### 8.10 `tracker review`

AI daily review / roast (`tracker/cli/formatters.py:14`, `tracker/ai/prompts.py:8`).

```bash
tracker review [--no-stream]
```

- Requires at least one activity logged today; otherwise `No activities logged today. Log something first!`
- Requires `api_key` in config; otherwise `No API key configured. Run 'tracker init' and set your key.`
- Builds a prompt containing activities, goals, completed, scores, sleep uptime, and day context (`tracker/ai/prompts.py:20`).
- Calls `AIClient.ask()` with `system_prompt="You are a brutally honest life coach who also considers sleep patterns and day context."` (`tracker/cli/formatters.py:33`).
- **Streaming is ON by default** — chunks print bold-live; `--no-stream` buffers and prints once (`tracker/ai/client.py:92`, `tracker/ai/client.py:161`).

Prompt asks the model for: harsh day rating /10, biggest time sink, what to do differently, one carry-forward, BS call-out — under 150 words.

### 8.11 `tracker week` / `tracker month`

Generate reports + optional AI analysis.

```bash
tracker week [--no-stream]
tracker month [--no-stream]
```

- `week` (`tracker/services/report_service.py:34`) collects Mon–Sun logs (`tracker/services/report_service.py:8`), writes `~/tracker/weekly/YYYY-Www.md`, prints `Weekly report saved: ...` + the concatenated logs. If AI is configured, it additionally calls `weekly_analysis_prompt()` (`tracker/ai/prompts.py:51`) with `You are a brutally honest productivity coach.` (`tracker/cli/formatters.py:62`).
- `month` (`tracker/services/report_service.py:45`) collects days 1–31 of the current month (`tracker/services/report_service.py:20`), writes `~/tracker/monthly/YYYY-MM.md`, then AI-analyzes via `monthly_analysis_prompt()` (first 4000 chars, `tracker/ai/prompts.py:66`) with `You are a brutally honest life coach.` (`tracker/cli/formatters.py:86`).
- Both respect `--no-stream` like `review`.

### 8.12 `tracker search`

Keyword search across all daily logs (`tracker/services/search_service.py:6`).

```bash
tracker search <keyword>
```

- Case-insensitive substring match across `~/tracker/daily/**/*.md`.
- Groups results by date: `📅 YYYY-MM-DD — N match(es)` plus up to 5 matching lines per file.
- No logs → `No logs found.` · No hits → `No matches for '...'`.

Example:

```bash
tracker search networking
# 📅 2026-09-09 — 2 match(es)
#    | 09:15 | Study networking | 60m | study | CIDR |
#    | 14:00 | Networking lab | 45m | work | subnetting |
```

### 8.13 `tracker export`

Export today's structured data as JSON (`tracker/services/export_service.py:8`).

```bash
tracker export [format]
```

- Only `json` is supported; other values → `Export format '...' not yet supported (use json).`
- Parses today's log via `parse_entries()` (`tracker/models/daily_log.py:180`) — activities, goals, completed, scores — adds `"date": "YYYY-MM-DD"`, writes to `~/tracker/export/YYYY-MM-DD.json` (`tracker/storage/file_storage.py:60`).

Example exported JSON:

```json
{
  "activities": [
    {"time": "09:15", "activity": "Study networking", "duration": "30m", "type": "work", "notes": ""}
  ],
  "goals": ["Learn subnetting"],
  "completed": [],
  "scores": {"productivity": 0, "energy": 0, "mood": 0},
  "accomplished": "",
  "learnings": "",
  "wins": "",
  "struggles": "",
  "date": "2026-09-10"
}
```

---

## 9. AI Features

| Command | Prompt Builder | System Prompt | Data Sent |
|---|---|---|---|
| `review` | `daily_review_prompt()` (`tracker/ai/prompts.py:8`) | `brutally honest life coach who also considers sleep patterns and day context` | Today's activities + goals + scores + sleep + day context |
| `week` | `weekly_analysis_prompt(data)` (`tracker/ai/prompts.py:51`) | `brutally honest productivity coach` | Collected Mon–Sun logs |
| `month` | `monthly_analysis_prompt(data)` (`tracker/ai/prompts.py:64`) | `brutally honest life coach` | Collected month logs (truncated to 4000 chars) |

**Client behavior** (`tracker/ai/client.py:21`):

- Endpoint: `https://openrouter.ai/api/v1/chat/completions`
- Model: `config.json → model` (default `openrouter/free`)
- `max_tokens: 16384`, `temperature: 0.7`, timeout 600 s, 3 retries.
- Retries on network errors (exponential back-off) and HTTP 429 (honors `Retry-After` header) (`tracker/ai/client.py:72`).
- HTTP 401 → `Invalid API key (401). Check the api_key in ~/tracker/config.json`.
- Streaming (`stream: true` default) parses SSE `data:` lines, renders `reasoning_content` dim and `content` bold live (`tracker/ai/client.py:113`).
- Without a key, `create_client()` returns `None` (`tracker/ai/client.py:193`); AI sections are skipped with a warning.

---

## 10. Typical Workflows

### Morning routine

```bash
tracker today                          # see plan
tracker goal "Finish ch.4 — TCP"
tracker sleep --wakeup 06:30           # log wake
tracker special college --notes "DBMS lab"
```

### During the day

```bash
tracker log "DBMS lab" 120 work --notes "joins + indexing"
tracker log "Lunch" 30 eat
tracker log "YouTube" 40 wasted        # honesty matters
tracker habit "Drink water"
```

### Evening shutdown

```bash
tracker stats                          # check progress bar
tracker review                         # AI roast — be honest, it helps
tracker sleep --bedtime 23:00
```

### Weekly / Monthly close

```bash
tracker week                           # writes ~/tracker/weekly/YYYY-Www.md + AI analysis
tracker month                          # writes ~/tracker/monthly/YYYY-MM.md + AI analysis
tracker export json                    # backup today's structured data
```

### Project work

```bash
tracker project my-app
# edit ~/tracker/projects/my-app/progress.md directly
tracker log "Built auth module" 90 work --notes "project:my-app"
```

### Searching history

```bash
tracker search "subnetting"
tracker search "wasted"
```

---

## 11. Tips & Reference

- **Quoting:** always quote multi-word activities: `tracker log "Study networking" 30 work`.
- **Interactive fallback:** any `log` / `sleep` / `special` / `habit` invocation with missing required args drops into prompts — handy when you forget syntax.
- **Editing logs by hand:** the markdown files are yours. Fix a typo or reorder a table directly in your editor; Tracker re-reads the file on next command.
- **Target tuning:** edit `daily_target_hours` in `~/tracker/config.json` to adjust the progress bar in `tracker stats`.
- **Model choice:** set `"model": "openai/gpt-4o-mini"` (or any OpenRouter id) in `config.json` to change the coach.
- **Backups:** `cp -r ~/tracker ~/tracker.bak` or `git init` inside `~/tracker` — all data is plain text.
- **Scores:** `set_scores()` (`tracker/models/daily_log.py:152`) is available programmatically; CLI score editing can be added by editing that file.
- **Habit best:** `best` never decreases — it tracks the all-time longest streak (`tracker/models/habit.py:58`).
- **Time parsing:** `HH:MM` accepts `9:05` or `09:05`; hours 0–23, minutes 00–59 (`tracker/utils/time_utils.py:8`).

---

## 12. Troubleshooting & FAQ

**`FileNotFoundError: Run 'tracker init' first.`**
→ You deleted or never created `~/tracker/config.json`. Run `tracker init`.

**`No activities logged today. Log something first!` on `tracker review`**
→ `review` requires at least one Time Log row today (`tracker/cli/formatters.py:19`).

**`No API key configured.`**
→ Set `api_key` in `~/tracker/config.json` or re-run `tracker init` and paste your OpenRouter key.

**`Invalid API key (401).` / `Rate limited (429).` / `HTTP 4xx/5xx`**
→ Printed by `AIClient.ask()` (`tracker/ai/client.py:83`). Check `config.json → api_key`, verify the key at openrouter.ai, and wait before retrying on 429.

**`Invalid time format. Use HH:MM (e.g. 23:00).`**
→ Bedtime/wakeup must match `H:MM` or `HH:MM` with valid ranges (`tracker/utils/time_utils.py:11`).

**`Invalid day type.`**
→ Only `exam`, `college`, `holiday`, `normal` are accepted (`tracker/models/day_context.py:10`).

**`Goal '...' not found.`**
→ `tracker done` requires an exact string match to a `- [ ]` line (`tracker/models/daily_log.py:143`). Copy-paste from `tracker today`.

**`Export format '...' not yet supported`**
→ Only `json` is implemented (`tracker/services/export_service.py:10`).

**Habit streak didn't increment?**
→ Streak increments only if `last_done == yesterday` (`tracker/models/habit.py:53`). Logging twice in one day is a no-op; skipping a day resets to 1.

**Display customization**
→ Colors and formatting come from `tracker/utils/markdown.py:6` (ANSI codes) and `fmt_bold()` / `heading()` / `ok()` / `err()`. Edit those to theme the CLI.

**Need help?**
→ `tracker --help` and `tracker <command> --help` always reflect the current parser (`tracker/cli/parser.py:6`). File an issue at the repository that contains `pyproject.toml:5`.

---

*Generated for Tracker `2.0.0` — see `tracker/__init__.py:3`, `tracker/main.py:1`, and `tracker/config.py:1` for authoritative source.*
