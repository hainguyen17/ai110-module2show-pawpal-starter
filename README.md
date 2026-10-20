# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py` (owner Jordan, 90 minutes available, two pets, tasks added out of order):

```

Today's Schedule for Jordan (80/90 min used)
--------------------------------------------
08:00  Feeding            Luna    10 min  [high] (todo, due 2026-10-20)
08:00  Morning walk       Mochi   30 min  [high] (todo, due 2026-10-20)
12:00  Give medication    Luna     5 min  [high] (todo, due 2026-10-20)
18:00  Brush coat         Mochi   20 min  [low] (todo, due 2026-10-20)
19:00  Laser play         Luna    15 min  [medium] (todo, due 2026-10-20)
Skipped (not enough time): Training session (Mochi)

Why this plan?
--------------
- Give medication (Luna): scheduled: high priority, fits (85 min left)
- Feeding (Luna): scheduled: high priority, fits (75 min left)
- Morning walk (Mochi): scheduled: high priority, fits (45 min left)
- Laser play (Luna): scheduled: medium priority, fits (30 min left)
- Training session (Mochi): skipped: needs 45 min but only 30 min left
- Brush coat (Mochi): scheduled: low priority, fits (10 min left)

Conflict warnings
-----------------
Warning: Feeding at 08:00 overlaps Morning walk at 08:00 (Luna and Mochi)

All tasks sorted by time (added out of order)
---------------------------------------------
08:00  Morning walk       Mochi   30 min  [high] (todo, due 2026-10-20)
08:00  Feeding            Luna    10 min  [high] (todo, due 2026-10-20)
12:00  Give medication    Luna     5 min  [high] (todo, due 2026-10-20)
18:00  Brush coat         Mochi   20 min  [low] (todo, due 2026-10-20)
19:00  Laser play         Luna    15 min  [medium] (todo, due 2026-10-20)
--:--  Training session   Mochi   45 min  [medium] (todo, due 2026-10-20)

Filter: Luna's tasks
--------------------
19:00  Laser play         Luna    15 min  [medium] (todo, due 2026-10-20)
12:00  Give medication    Luna     5 min  [high] (todo, due 2026-10-20)
08:00  Feeding            Luna    10 min  [high] (todo, due 2026-10-20)

Recurring: complete the daily Morning walk
------------------------------------------
Completed: Morning walk (due 2026-10-20)
Next occurrence created: Morning walk, due 2026-10-21

Filter: completed tasks / still-to-do tasks
-------------------------------------------
done: ['Morning walk']
todo: ['Brush coat', 'Training session', 'Morning walk', 'Laser play', 'Give medication', 'Feeding']
```

## 🧩 Implementation Summary

The logic layer lives in `pawpal_system.py` and has four classes:

- **Task** (dataclass): one care activity with a title, duration, priority, optional preferred time (`HH:MM`), frequency and completion flag.
- **Pet** (dataclass): a pet's name and species, plus its list of tasks.
- **Owner** (dataclass): the daily time budget and the owner's pets. `get_all_tasks()` returns every pet's tasks together.
- **Scheduler**: reads tasks through `Owner.get_all_tasks()`, so it plans across all pets. `generate_plan()` takes pending tasks due today by priority (then shortest first) until the time budget runs out, then orders the result by preferred time. It also sorts, filters, detects conflicts, completes recurring tasks, and explains the plan (see Smarter Scheduling below).

`main.py` is a terminal demo of these classes. The Streamlit UI in `app.py` imports them and keeps one `Owner` in `st.session_state`, so pets and tasks you add persist across reruns. Run it with `streamlit run app.py`.

Known limit: `Owner.preferences` is not used by the scheduler yet.

## 🧪 Testing PawPal+

```bash
python -m pytest
```

**What the 18 tests cover**

- **Sorting:** tasks come back in chronological `HH:MM` order, with untimed tasks last.
- **Recurrence:** completing a daily task creates a copy due the next day, and a weekly task creates one due 7 days out. One-off tasks and double completion create nothing.
- **Conflict detection:** overlapping windows are flagged (same pet and across pets), identical start times are flagged, and back-to-back tasks are not.
- **Planning:** high priority wins when time is short, completed and future-dated tasks are excluded, and a zero-minute budget skips everything.
- **Edge cases:** a pet with no tasks, an owner with no pets, and filtering by pet and status.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/tiffanymhai/Developer/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 18 items

tests/test_pawpal.py ..................                                  [100%]

============================== 18 passed in 0.02s ==============================
```

**Confidence level: ⭐⭐⭐⭐ (4/5).** All core behaviors and the main edge cases pass. Not yet tested: malformed `HH:MM` strings, tasks that cross midnight, and `Owner.preferences` (unused by the scheduler).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by `"HH:MM"` preferred time using `sorted()` with a lambda key. Untimed tasks go last, and ties keep their existing (priority) order because the sort is stable. `generate_plan()` uses it for the final plan. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Returns tasks for one pet, one completion status, or both. Either argument left as `None` means no filter on it. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.conflict_warnings()` | Compares every pair of planned, timed tasks and flags any whose start-to-end windows overlap (same pet or different pets). `conflict_warnings()` returns readable messages, so nothing crashes. Back-to-back tasks (8:00 for 30 min, then 8:30) are not a conflict. |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Completing a `daily` or `weekly` task returns a fresh copy due today + 1 day (or + 7 days) via `timedelta`, and the scheduler adds it to the same pet. Completing a task twice does not create a duplicate. |
| Due dates | `Scheduler.generate_plan()` | Only tasks due today or earlier are planned, so tomorrow's recurring copy does not show up in today's plan. |

Tradeoff: conflicts are only reported, not resolved, and only tasks that made it into the plan are checked. See `reflection.md`, section 2b.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
