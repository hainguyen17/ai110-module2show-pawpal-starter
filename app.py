import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planner: add pets and tasks, then build a daily plan that fits your time.")

# Streamlit re-runs this script on every interaction, so the Owner is kept in
# session_state and only created the first time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=90)
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes_per_day = int(
        st.number_input(
            "Minutes available today",
            min_value=1,
            max_value=1440,
            value=owner.available_minutes_per_day,
        )
    )

st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()} the {species}.")
        else:
            st.error("Please enter a pet name.")

if owner.pets:
    st.write(", ".join(f"{p.name} ({p.species}, {len(p.tasks)} tasks)" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.subheader("Tasks")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        col1, col2 = st.columns(2)
        with col1:
            preferred = st.time_input("Preferred time (optional)", value=None)
        with col2:
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == pet_choice)
            pet.add_task(
                Task(
                    title=task_title.strip() or "Untitled task",
                    duration_minutes=int(duration),
                    priority=priority,
                    preferred_time=preferred.strftime("%H:%M") if preferred else None,
                    frequency=frequency,
                )
            )
            st.success(f'Added "{task_title}" to {pet_choice}.')
else:
    st.caption("Add a pet first, then you can give it tasks.")


def task_rows(tasks: list[Task]) -> list[dict]:
    return [
        {
            "time": t.preferred_time or "-",
            "task": t.title,
            "pet": scheduler.pet_name_for(t),
            "minutes": t.duration_minutes,
            "priority": t.priority,
            "repeats": t.frequency,
            "due": t.due_date.isoformat(),
            "done": "yes" if t.completed else "no",
        }
        for t in tasks
    ]


if owner.get_all_tasks():
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
    st.markdown("#### Your tasks (sorted by time)")
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "To do", "Done"])
    shown = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "To do": False, "Done": True}[status_filter],
    )
    if shown:
        st.table(task_rows(scheduler.sort_by_time(shown)))
    else:
        st.info("No tasks match this filter.")

    todo = scheduler.filter_tasks(completed=False)
    if todo:
        col1, col2 = st.columns([3, 1])
        with col1:
            to_complete = st.selectbox(
                "Mark a task complete",
                range(len(todo)),
                format_func=lambda i: f"{todo[i].title} ({scheduler.pet_name_for(todo[i])})",
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("Complete"):
                task = todo[to_complete]
                next_task = scheduler.mark_task_complete(task)
                if next_task:
                    st.session_state.flash = (
                        f'Done! "{task.title}" repeats {task.frequency}, '
                        f"so the next one is due {next_task.due_date}."
                    )
                else:
                    st.session_state.flash = f'Done! "{task.title}" is complete.'
                st.rerun()
else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if not plan:
        st.warning("Nothing to schedule today. Add some tasks first.")
    else:
        used = sum(t.duration_minutes for t in plan)
        st.success(f"{used} of {owner.available_minutes_per_day} minutes planned for today.")
        st.table(task_rows(plan))

    if scheduler.skipped:
        st.warning(
            "Not enough time for: "
            + ", ".join(f"{t.title} ({scheduler.pet_name_for(t)})" for t in scheduler.skipped)
            + ". Raise your available minutes or lower their priority."
        )

    conflicts = scheduler.conflict_warnings()
    if conflicts:
        st.error(f"⚠️ {len(conflicts)} scheduling conflict(s) found")
        for warning in conflicts:
            st.warning(warning)
        st.caption(
            "These tasks overlap in time. Move one to a different preferred time "
            "(or ask someone to help) so nothing gets missed."
        )
    elif plan:
        st.success("No time conflicts. You're good to go!")

    with st.expander("Why this plan?", expanded=False):
        st.text(scheduler.explain_plan())
