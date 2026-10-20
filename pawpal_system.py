"""PawPal+ core domain model: tasks, pets, owner, and the scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from itertools import combinations
from typing import Literal, Optional

Priority = Literal["high", "medium", "low"]
Frequency = Literal["once", "daily", "weekly"]

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


def _to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, grooming, ...)."""

    title: str
    duration_minutes: int
    priority: Priority = "medium"
    preferred_time: Optional[str] = None  # "HH:MM", 24-hour
    frequency: Frequency = "once"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self, today: Optional[date] = None) -> Optional["Task"]:
        """Mark this task done; for daily/weekly tasks return a fresh copy due next time."""
        if self.completed:
            return None
        self.completed = True
        interval = RECURRENCE_DAYS.get(self.frequency)
        if interval is None:
            return None
        next_due = (today or date.today()) + timedelta(days=interval)
        return replace(self, completed=False, due_date=next_due)


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """The pet owner: daily time budget, preferences, and their pets."""

    name: str
    available_minutes_per_day: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily plan from an owner's tasks and constraints."""

    def __init__(self, owner: Owner, today: Optional[date] = None) -> None:
        self.owner = owner
        self.today = today or date.today()
        self.skipped: list[Task] = []
        self._reasons: list[tuple[Task, str]] = []

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks ordered by "HH:MM" preferred time, with untimed tasks last."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        # "HH:MM" strings sort correctly as text; the tuple pushes None to the end.
        return sorted(tasks, key=lambda t: (t.preferred_time is None, t.preferred_time or ""))

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> list[Task]:
        """Return tasks for one pet and/or one completion status; None means no filter."""
        return [
            task
            for pet in self.owner.pets
            if pet_name is None or pet.name == pet_name
            for task in pet.tasks
            if completed is None or task.completed == completed
        ]

    def generate_plan(self) -> list[Task]:
        """Pick the highest-priority tasks due today that fit the time budget, ordered by time."""
        self.skipped = []
        self._reasons = []
        remaining = self.owner.available_minutes_per_day
        pending = [
            t for t in self.owner.get_all_tasks() if not t.completed and t.due_date <= self.today
        ]
        pending.sort(key=lambda t: (PRIORITY_RANK[t.priority], t.duration_minutes))

        plan: list[Task] = []
        for task in pending:
            if task.duration_minutes <= remaining:
                remaining -= task.duration_minutes
                plan.append(task)
                self._reasons.append(
                    (task, f"scheduled: {task.priority} priority, fits ({remaining} min left)")
                )
            else:
                self.skipped.append(task)
                self._reasons.append(
                    (task, f"skipped: needs {task.duration_minutes} min but only {remaining} min left")
                )

        # Sorting is stable, so tasks at the same time (or untimed) stay in priority order.
        return self.sort_by_time(plan)

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of planned tasks whose time slots overlap (same or different pets)."""
        timed = [t for t in self.generate_plan() if t.preferred_time]

        def overlaps(a: Task, b: Task) -> bool:
            a_start, b_start = _to_minutes(a.preferred_time), _to_minutes(b.preferred_time)
            return a_start < b_start + b.duration_minutes and b_start < a_start + a.duration_minutes

        return [(a, b) for a, b in combinations(timed, 2) if overlaps(a, b)]

    def conflict_warnings(self) -> list[str]:
        """Return a readable warning for each overlap instead of raising an error."""
        warnings = []
        for a, b in self.detect_conflicts():
            pet_a, pet_b = self.pet_name_for(a), self.pet_name_for(b)
            who = f"for {pet_a}" if pet_a == pet_b else f"({pet_a} and {pet_b})"
            warnings.append(
                f"Warning: {a.title} at {a.preferred_time} overlaps {b.title} "
                f"at {b.preferred_time} {who}"
            )
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and, if it recurs, add its next occurrence to the same pet."""
        pet = self._pet_of(task)
        next_task = task.mark_complete(self.today)
        if pet is not None and next_task is not None:
            pet.add_task(next_task)
        return next_task

    def _pet_of(self, task: Task) -> Optional[Pet]:
        """Find the pet that owns this exact task object."""
        return next((p for p in self.owner.pets if any(t is task for t in p.tasks)), None)

    def pet_name_for(self, task: Task) -> str:
        """Return the name of the pet that owns this task."""
        pet = self._pet_of(task)
        return pet.name if pet else "unknown"

    def explain_plan(self) -> str:
        """Explain why each task was scheduled or skipped."""
        self.generate_plan()
        if not self._reasons:
            return "No pending tasks to plan."
        return "\n".join(
            f"- {task.title} ({self.pet_name_for(task)}): {reason}"
            for task, reason in self._reasons
        )
