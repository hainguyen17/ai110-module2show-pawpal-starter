# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  PawPal+ helps a busy pet owner stay consistent with pet care. The core user needs are: (1) record the pet's care tasks, (2) tell the app how much time they have and what they prefer, and (3) get a daily plan with an explanation of why it was chosen. I started from those needs and kept one class per concept: the people and animals (Owner, Pet), the work to be done (Task), and the planning logic (Scheduler). Owner has many Pets, a Pet has many Tasks, and the Scheduler reads from the Owner to build the plan. The Streamlit UI only calls these classes and holds no scheduling logic.

- What classes did you include, and what responsibilities did you assign to each?
  - **Task**: one care activity (walk, feeding, meds, enrichment, grooming). Holds title, duration, priority, category, an optional preferred time, a completed flag and an optional frequency (daily/weekly). Duration and priority are the minimum the scheduler needs, so they are required.
  - **Pet**: holds the pet's basic info (name, species, age) and owns its list of Tasks. It can add, remove and list pending tasks. Putting tasks here lets one owner have several pets.
  - **Owner**: holds the owner's constraints, meaning the time available per day and preferences (for example, no walks late at night), plus their Pets. Constraints live here so the Scheduler stays reusable.
  - **Scheduler**: the only class that makes decisions. It collects the owner's tasks, sorts them by priority then duration, fits them into the available time, flags overlapping slots, handles recurring tasks, and produces an explanation for each task it scheduled or skipped. Keeping this in one place makes it easy to unit test.

  I kept the scope to four classes to keep the first version small. If the explanation output gets awkward, I would add a small `ScheduledItem` (task, start time, reason) as a fifth class rather than returning loose tuples.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
