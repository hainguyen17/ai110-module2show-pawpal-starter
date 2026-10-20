"""Temporary terminal demo for the PawPal+ logic layer."""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner(name="Jordan", available_minutes_per_day=90)

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", preferred_time="08:00", frequency="daily"))
    mochi.add_task(Task("Brush coat", 20, "low", preferred_time="18:00"))
    mochi.add_task(Task("Training session", 45, "medium"))
    luna.add_task(Task("Feeding", 10, "high", preferred_time="08:15", frequency="daily"))
    luna.add_task(Task("Give medication", 5, "high", preferred_time="12:00"))
    luna.add_task(Task("Laser play", 15, "medium", preferred_time="19:00"))
    return owner


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    planned = sum(t.duration_minutes for t in plan)

    print(f"Today's Schedule for {owner.name} "
          f"({planned}/{owner.available_minutes_per_day} min used)")
    print("-" * 56)
    for task in plan:
        time = task.preferred_time or "--:--"
        print(f"{time}  {task.title:<18} {scheduler.pet_name_for(task):<6} "
              f"{task.duration_minutes:>3} min  [{task.priority}]")

    if scheduler.skipped:
        print("\nSkipped (not enough time):")
        for task in scheduler.skipped:
            print(f"  {task.title} ({scheduler.pet_name_for(task)}, {task.duration_minutes} min)")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nTime conflicts:")
        for a, b in conflicts:
            print(f"  {a.title} ({a.preferred_time}) overlaps {b.title} ({b.preferred_time})")

    print("\nWhy this plan:")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
