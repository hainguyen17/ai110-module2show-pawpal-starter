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

Output of `python main.py` (owner Jordan, 90 minutes available, two pets):

```
Today's Schedule for Jordan (80/90 min used)
--------------------------------------------------------
08:00  Morning walk       Mochi   30 min  [high]
08:15  Feeding            Luna    10 min  [high]
12:00  Give medication    Luna     5 min  [high]
18:00  Brush coat         Mochi   20 min  [low]
19:00  Laser play         Luna    15 min  [medium]

Skipped (not enough time):
  Training session (Mochi, 45 min)

Time conflicts:
  Morning walk (08:00) overlaps Feeding (08:15)

Why this plan:
- Give medication (Luna): scheduled: high priority, fits (85 min left)
- Feeding (Luna): scheduled: high priority, fits (75 min left)
- Morning walk (Mochi): scheduled: high priority, fits (45 min left)
- Laser play (Luna): scheduled: medium priority, fits (30 min left)
- Training session (Mochi): skipped: needs 45 min but only 30 min left
- Brush coat (Mochi): scheduled: low priority, fits (10 min left)
```

## 🧩 Implementation Summary

The logic layer lives in `pawpal_system.py` and has four classes:

- **Task** (dataclass): one care activity with a title, duration, priority, optional preferred time (`HH:MM`), frequency and completion flag.
- **Pet** (dataclass): a pet's name and species, plus its list of tasks.
- **Owner** (dataclass): the daily time budget and the owner's pets. `get_all_tasks()` returns every pet's tasks together.
- **Scheduler**: reads tasks through `Owner.get_all_tasks()`, so it plans across all pets. `generate_plan()` takes pending tasks by priority (then shortest first) until the time budget runs out, then orders the result by preferred time. `detect_conflicts()` finds overlapping slots, and `explain_plan()` says why each task was scheduled or skipped.

`main.py` is a terminal demo of these classes. The Streamlit UI in `app.py` is not connected to them yet.

Known limits: `frequency` is stored but recurring tasks are not generated, and `Owner.preferences` is not used by the scheduler yet.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
collected 6 items

tests/test_pawpal.py ......                                              [100%]

============================== 6 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
