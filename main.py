"""Temporary terminal demo for the PawPal+ logic layer."""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner(name="Jordan", available_minutes_per_day=90)

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of time order on purpose, to show sorting.
    mochi.add_task(Task("Brush coat", 20, "low", preferred_time="18:00"))
    mochi.add_task(Task("Training session", 45, "medium"))
    mochi.add_task(Task("Morning walk", 30, "high", preferred_time="08:00", frequency="daily"))
    luna.add_task(Task("Laser play", 15, "medium", preferred_time="19:00"))
    luna.add_task(Task("Give medication", 5, "high", preferred_time="12:00", frequency="weekly"))
    luna.add_task(Task("Feeding", 10, "high", preferred_time="08:00", frequency="daily"))
    return owner


def line(task: Task, scheduler: Scheduler) -> str:
    time = task.preferred_time or "--:--"
    status = "done" if task.completed else "todo"
    return (f"{time}  {task.title:<18} {scheduler.pet_name_for(task):<6} "
            f"{task.duration_minutes:>3} min  [{task.priority}] ({status}, due {task.due_date})")


def section(title: str) -> None:
    print(f"\n{title}\n" + "-" * len(title))


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    planned = sum(t.duration_minutes for t in plan)

    section(f"Today's Schedule for {owner.name} "
            f"({planned}/{owner.available_minutes_per_day} min used)")
    for task in plan:
        print(line(task, scheduler))
    if scheduler.skipped:
        print("Skipped (not enough time): "
              + ", ".join(f"{t.title} ({scheduler.pet_name_for(t)})" for t in scheduler.skipped))

    section("Why this plan?")
    print(scheduler.explain_plan())

    section("Conflict warnings")
    for warning in scheduler.conflict_warnings() or ["No conflicts."]:
        print(warning)

    section("All tasks sorted by time (added out of order)")
    for task in scheduler.sort_by_time():
        print(line(task, scheduler))

    section("Filter: Luna's tasks")
    for task in scheduler.filter_tasks(pet_name="Luna"):
        print(line(task, scheduler))

    section("Recurring: complete the daily Morning walk")
    walk = next(t for t in scheduler.filter_tasks() if t.title == "Morning walk")
    next_walk = scheduler.mark_task_complete(walk)
    print(f"Completed: {walk.title} (due {walk.due_date})")
    print(f"Next occurrence created: {next_walk.title}, due {next_walk.due_date}")

    section("Filter: completed tasks / still-to-do tasks")
    print("done:", [t.title for t in scheduler.filter_tasks(completed=True)])
    print("todo:", [t.title for t in scheduler.filter_tasks(completed=False)])


if __name__ == "__main__":
    main()
