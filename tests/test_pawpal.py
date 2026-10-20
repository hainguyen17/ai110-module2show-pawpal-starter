from datetime import date

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


def _owner_with_pets():
    owner = Owner("Jordan", 240)
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat


def test_sort_by_time_orders_hhmm_and_puts_untimed_last():
    owner, dog, _ = _owner_with_pets()
    for title, time in [("Evening", "18:00"), ("Untimed", None), ("Early", "07:30"), ("Noon", "12:00")]:
        dog.add_task(Task(title, 10, preferred_time=time))

    ordered = Scheduler(owner).sort_by_time()

    assert [t.title for t in ordered] == ["Early", "Noon", "Evening", "Untimed"]


def test_filter_tasks_by_pet_and_status():
    owner, dog, cat = _owner_with_pets()
    walk, feed = Task("Walk", 30), Task("Feeding", 10)
    dog.add_task(walk)
    cat.add_task(feed)
    walk.mark_complete()
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(pet_name="Luna") == [feed]
    assert scheduler.filter_tasks(completed=True) == [walk]
    assert scheduler.filter_tasks(pet_name="Mochi", completed=False) == []


def test_completing_daily_task_creates_next_day_copy():
    owner, dog, _ = _owner_with_pets()
    today = date(2026, 10, 20)
    walk = Task("Walk", 30, frequency="daily", due_date=today)
    dog.add_task(walk)

    next_task = Scheduler(owner, today).mark_task_complete(walk)

    assert walk.completed is True
    assert next_task.due_date == date(2026, 10, 21)
    assert next_task.completed is False
    assert next_task in dog.tasks


def test_completing_weekly_task_creates_copy_seven_days_out():
    owner, dog, _ = _owner_with_pets()
    today = date(2026, 10, 20)
    bath = Task("Bath", 30, frequency="weekly", due_date=today)
    dog.add_task(bath)

    next_task = Scheduler(owner, today).mark_task_complete(bath)

    assert next_task.due_date == date(2026, 10, 27)


def test_completing_one_off_or_already_done_task_creates_nothing():
    owner, dog, _ = _owner_with_pets()
    once = Task("Vet visit", 60)
    daily = Task("Walk", 30, frequency="daily")
    dog.add_task(once)
    dog.add_task(daily)
    scheduler = Scheduler(owner)

    assert scheduler.mark_task_complete(once) is None
    scheduler.mark_task_complete(daily)
    assert scheduler.mark_task_complete(daily) is None  # second completion adds no duplicate
    assert len(dog.tasks) == 3


def test_future_dated_task_is_not_in_todays_plan():
    owner, dog, _ = _owner_with_pets()
    today = date(2026, 10, 20)
    dog.add_task(Task("Walk", 30, due_date=date(2026, 10, 21)))

    assert Scheduler(owner, today).generate_plan() == []


def test_conflict_warning_for_same_time_across_pets():
    owner, dog, cat = _owner_with_pets()
    dog.add_task(Task("Walk", 30, preferred_time="08:00"))
    cat.add_task(Task("Feeding", 10, preferred_time="08:00"))

    warnings = Scheduler(owner).conflict_warnings()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feeding" in warnings[0]
    assert "Mochi" in warnings[0] and "Luna" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    owner, dog, _ = _owner_with_pets()
    dog.add_task(Task("Walk", 30, preferred_time="08:00"))
    dog.add_task(Task("Feeding", 10, preferred_time="08:30"))

    assert Scheduler(owner).conflict_warnings() == []


def test_pet_with_no_tasks_yields_empty_results():
    owner, _, _ = _owner_with_pets()
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.conflict_warnings() == []
    assert scheduler.explain_plan() == "No pending tasks to plan."


def test_owner_with_no_pets_yields_empty_plan():
    assert Scheduler(Owner("Jordan", 60)).generate_plan() == []


def test_identical_start_times_are_flagged_and_keep_priority_order():
    owner, dog, _ = _owner_with_pets()
    low = Task("Brush", 10, "low", preferred_time="08:00")
    high = Task("Meds", 10, "high", preferred_time="08:00")
    dog.add_task(low)
    dog.add_task(high)
    scheduler = Scheduler(owner)

    assert [t.title for t in scheduler.generate_plan()] == ["Meds", "Brush"]
    assert len(scheduler.detect_conflicts()) == 1


def test_zero_time_budget_skips_everything():
    owner = Owner("Jordan", 0)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high"))
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan() == []
    assert len(scheduler.skipped) == 1
