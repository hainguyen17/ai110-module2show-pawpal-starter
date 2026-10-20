from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10))

    assert len(pet.tasks) == 1


def test_scheduler_reads_tasks_from_all_pets():
    owner = Owner("Jordan", 120)
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Walk", 30, "high"))
    cat.add_task(Task("Feeding", 10, "high"))

    plan = Scheduler(owner).generate_plan()

    assert {t.title for t in plan} == {"Walk", "Feeding"}


def test_plan_prefers_high_priority_when_time_is_short():
    owner = Owner("Jordan", 30)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Brush coat", 30, "low"))
    pet.add_task(Task("Give medication", 30, "high"))
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan()

    assert [t.title for t in plan] == ["Give medication"]
    assert [t.title for t in scheduler.skipped] == ["Brush coat"]


def test_plan_ignores_completed_tasks():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    done = Task("Walk", 30, "high")
    done.mark_complete()
    pet.add_task(done)

    assert Scheduler(owner).generate_plan() == []


def test_detect_conflicts_flags_overlapping_times():
    owner = Owner("Jordan", 120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    walk = Task("Walk", 30, "high", preferred_time="08:00")
    feed = Task("Feeding", 10, "high", preferred_time="08:15")
    play = Task("Play", 10, "medium", preferred_time="09:00")
    for t in (walk, feed, play):
        pet.add_task(t)

    conflicts = Scheduler(owner).detect_conflicts()

    assert conflicts == [(walk, feed)]
