"""PawPal+ core domain model. Skeleton only: attributes and method stubs, no logic yet."""

from dataclasses import dataclass, field
from typing import Literal, Optional

Priority = Literal["high", "medium", "low"]
Frequency = Literal["once", "daily", "weekly"]


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
        raise NotImplementedError


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        raise NotImplementedError

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner: daily time budget, preferences, and their pets."""

    name: str
    available_minutes_per_day: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Builds and explains a daily plan from an owner's tasks and constraints."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_plan(self) -> list[Task]:
        """Pick and order tasks that fit the owner's available time."""
        raise NotImplementedError

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose time slots overlap."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Explain why each task was scheduled or skipped."""
        raise NotImplementedError
