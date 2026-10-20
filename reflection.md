# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  PawPal+ helps a busy pet owner stay consistent with pet care. The core user needs are: (1) record the pet's care tasks, (2) tell the app how much time they have and what they prefer, and (3) get a daily plan with an explanation of why it was chosen. I kept one class per concept: the people and animals (Owner, Pet), the work to be done (Task), and the planning logic (Scheduler). An Owner has many Pets and a Pet has many Tasks (composition, since each belongs to its parent). The Scheduler reads from the Owner to build the plan. The Streamlit UI only calls these classes and holds no scheduling logic.

- What classes did you include, and what responsibilities did you assign to each?
    - **Task** (dataclass): one care activity. Holds `title`, `duration_minutes`, `priority`, an optional `preferred_time`, a `frequency` and a `completed` flag, and can mark itself complete.
    - **Pet** (dataclass): holds `name` and `species` and owns its list of Tasks. It can add and remove tasks and list the pending ones.
    - **Owner** (dataclass): holds the daily time budget (`available_minutes_per_day`), `preferences` and the list of Pets. `get_all_tasks()` returns every pet's tasks together, so the Scheduler never has to look inside a single pet.
    - **Scheduler**: the only class that makes decisions. It builds the daily plan from the Owner's tasks, detects overlapping time slots, and explains why each task was scheduled or skipped.

**b. Design changes**

- Did your design change during implementation?
  Yes. Before writing any code I trimmed the first UML because it was over-engineered for the scenario. I removed `Task.category`, `Task.is_high_priority()`, `Pet.age`, `Scheduler.date`, a `handle_recurring()` method and an extra Scheduler-to-Task dependency line. During implementation I added back two small things: `Scheduler.skipped` and `Scheduler.pet_name_for()`. Without them the plan could not say which tasks were dropped, or which pet a task belongs to, because a Task does not know its Pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  It considers the owner's daily time budget, each task's priority, and each task's duration. It also uses `preferred_time` to order the final plan and to detect overlaps. `Owner.preferences` exists but the scheduler does not use it yet.
- How did you decide which constraints mattered most?
  The time budget is a hard limit, since a plan that does not fit in the day is useless. Priority decides what gets the limited time, because a missed medication matters more than a missed grooming session.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  It is greedy: it takes tasks in priority order (shortest first within a priority) and skips any task that does not fit in the time left, then keeps going with smaller ones. That does not always give the best possible use of the day, and it does not move tasks to avoid conflicts. It only reports them.
  A second tradeoff is conflict handling. The scheduler checks whether the time windows (start plus duration) of planned tasks overlap, which is more accurate than only comparing exact start times. But it only reports a warning and never moves a task, and it only checks tasks that made it into the plan.
- Why is that tradeoff reasonable for this scenario?
  A pet owner needs a plan that is simple to follow and easy to explain. The greedy rule is predictable, and each skipped task gets a plain-language reason. Finding the mathematically optimal plan would add complexity the scenario does not need.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  I used AI for design brainstorming (choosing the four classes from the scenario), drafting the Mermaid class diagram, generating the dataclass skeleton, implementing the scheduler, and drafting the demo script, tests and documentation.
- What kinds of prompts or questions were most helpful?
  Asking it to cross-check the design as a senior tech lead, and asking whether the relationships made sense and whether anything was over-engineered, gave the most useful feedback.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  The first UML the AI produced included extras such as a task category, a scheduler date and a recurring-task method. I asked for a review for over-engineering, and we cut them. Later the AI's first stub used `pass`, and I kept the safer `raise NotImplementedError` so unfinished methods fail loudly instead of returning `None`.
- How did you evaluate or verify what the AI suggested?
  I checked each class against the scenario in the README, ran `python main.py` to see a real multi-pet schedule with a skipped task and a conflict, and ran `python -m pytest`, where all 18 tests now pass.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  Marking a task complete, adding a task to a pet, the scheduler reading tasks from all pets, high priority winning when time is short, completed tasks being ignored, and overlapping times being flagged as conflicts. Later I added sorting by time, filtering, daily and weekly recurrence, future-dated tasks, back-to-back tasks, and edge cases such as a pet with no tasks, an owner with no pets, identical start times, and a zero-minute budget.
- Why were these tests important?
  They cover the behaviors the scheduler depends on most. The multi-pet and time-budget tests protect the core promise of the app: one plan across all pets that fits in the day.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  About 4 out of 5. All 18 tests pass and they cover the main behaviors and several edge cases.
- What edge cases would you test next if you had more time?
  Malformed `HH:MM` strings, tasks that run past midnight, and tasks with a duration of zero. The UI itself has only been checked by hand.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  Keeping all scheduling decisions in the `Scheduler` class, so the Streamlit UI and the terminal demo are thin and both show the same sorting, conflict and recurrence behavior.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  I would make the scheduler use `Owner.preferences`, and offer to resolve conflicts (for example by suggesting the nearest free slot) instead of only reporting them. I would also let the UI edit and delete tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  The AI is fast at producing code, but it tends to add more than the scenario needs. My job as lead architect was to decide what belongs (and what to cut), check each piece against the requirements, and verify with tests and a real run rather than trusting the output.

**d. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?
  Asking the assistant to review the design critically before coding, generating the class skeleton from the UML, and having it write and run tests against the real code. Running the tests and `main.py` after each change caught problems early.
- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
  The first UML included a task category, a scheduler date and a `handle_recurring()` method. I asked for an over-engineering review and cut them. Recurrence ended up as a small `Task.mark_complete()` that returns the next copy, with `Scheduler.mark_task_complete()` adding it to the right pet.
- How did using separate chat sessions for different phases help you stay organized?
  To help the AI think outside of the context it was given during previous phases. For example, a test agent would create more comprehensive test cases and not overly optimize for the implementation logic. Also, it frees up the context memory and can help the agent store more test related context.
- What did you learn about being the "lead architect" when collaborating with powerful AI tools?
  The AI proposes, but I own the design. Clear class responsibilities made it easy to judge each suggestion: if it did not fit one class's job or the scenario, it did not go in.
