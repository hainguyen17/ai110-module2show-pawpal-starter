"""PawPal+ core domain model: tasks, pets, owner, and the scheduler."""

from dataclasses import dataclass, field
from typing import Literal, Optional

Priority = Literal["high", "medium", "low"]
Frequency = Literal["once", "daily", "weekly"]

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


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

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.skipped: list[Task] = []
        self._reasons: list[tuple[Task, str]] = []

    def generate_plan(self) -> list[Task]:
        """Pick the highest-priority pending tasks that fit the time budget, ordered by time."""
        self.skipped = []
        self._reasons = []
        remaining = self.owner.available_minutes_per_day
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
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

        # Timed tasks first in clock order; untimed ones after, highest priority first.
        plan.sort(
            key=lambda t: (
                t.preferred_time is None,
                t.preferred_time or "",
                PRIORITY_RANK[t.priority],
            )
        )
        return plan

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of planned tasks whose time slots overlap."""
        timed = [t for t in self.generate_plan() if t.preferred_time]
        conflicts = []
        for i, a in enumerate(timed):
            a_start = _to_minutes(a.preferred_time)
            a_end = a_start + a.duration_minutes
            for b in timed[i + 1 :]:
                b_start = _to_minutes(b.preferred_time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts

    def pet_name_for(self, task: Task) -> str:
        """Return the name of the pet that owns this task."""
        for pet in self.owner.pets:
            if any(t is task for t in pet.tasks):
                return pet.name
        return "unknown"

    def explain_plan(self) -> str:
        """Explain why each task was scheduled or skipped."""
        self.generate_plan()
        if not self._reasons:
            return "No pending tasks to plan."
        return "\n".join(
            f"- {task.title} ({self.pet_name_for(task)}): {reason}"
            for task, reason in self._reasons
        )
