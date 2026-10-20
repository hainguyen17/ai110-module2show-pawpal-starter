import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Streamlit re-runs this script on every interaction, so the Owner is kept in
# session_state and only created the first time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=90)
owner: Owner = st.session_state.owner

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

st.markdown("### Tasks")
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
        preferred = st.time_input("Preferred time (optional)", value=None)
        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == pet_choice)
            pet.add_task(
                Task(
                    title=task_title.strip() or "Untitled task",
                    duration_minutes=int(duration),
                    priority=priority,
                    preferred_time=preferred.strftime("%H:%M") if preferred else None,
                )
            )
            st.success(f"Added \"{task_title}\" to {pet_choice}.")
else:
    st.caption("Add a pet first, then you can give it tasks.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": pet.name,
                "task": t.title,
                "minutes": t.duration_minutes,
                "priority": t.priority,
                "time": t.preferred_time or "-",
            }
            for pet in owner.pets
            for t in pet.tasks
        ]
    )
else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if not plan:
        st.warning("Nothing to schedule. Add some tasks first.")
    else:
        used = sum(t.duration_minutes for t in plan)
        st.success(f"{used} of {owner.available_minutes_per_day} minutes planned.")
        st.table(
            [
                {
                    "time": t.preferred_time or "-",
                    "task": t.title,
                    "pet": scheduler.pet_name_for(t),
                    "minutes": t.duration_minutes,
                    "priority": t.priority,
                }
                for t in plan
            ]
        )
    for warning in scheduler.conflict_warnings():
        st.warning(warning)
    with st.expander("Why this plan?", expanded=True):
        st.text(scheduler.explain_plan())
