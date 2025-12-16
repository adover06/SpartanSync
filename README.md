# SpartanSync

A simpler learning management system.

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:

   cd SpartanSync

2. **Create a virtual environment** (recommended):

   python3 -m venv venv

3. **Activate the virtual environment**:
     source venv/bin/activate

4. **Install dependencies**:

   pip install -r requirements.txt

5. **API Key**:

   Go to https://platform.openai.com/docs/quickstart, create a key and save it somewhere safe.

5. **Enviroment Variables**:

   Create a file called ".env" in the root directory and paste the following: OPENAI_API_KEY=\<your openai key from above>

## Run

1. **Make sure your virtual environment is activated** (see Installation step 3)

2. **Run the application**:
   python run.py


3. **Access the application**:
   Open your web browser and navigate to:

   http://localhost:5000

   http://127.0.0.1:5000

> The SQLite database is created automatically on first run. If you ever need to rebuild it manually, run `python create_db.py`.


## Features at a Glance

- **Authentication & Roles** – WTForms login/signup with Student, TA, or Instructor roles plus a dedicated sign-out page.
- **Dashboards** – Student dashboard tracks assignment status; instructor dashboard highlights upcoming items and ungraded submissions, with quick links into each course.
- **Assignments & Rubrics** – Instructors can create/delete assignments, define rubric criteria, and grade submissions; TAs help grade and edit rubrics but cannot publish or delete assignments.
- **Study Planner** - Uses OpenAI's module in python to create a simple study/work plan for completing assignments on time. It constructs a prompt from a series of db queries for assignments, submissions, and user customization.
- **Announcements** – Course-scoped or general announcements with list/detail views, instructor-only creation/deletion, and course badges everywhere.
- **Courses & Class Selection** – Instructors add courses; students choose which classes appear on the home page via “Manage My Classes”; every class card links to a course overview showing its assignments/announcements.
- **Auto-provisioned SQLite DB** – Database tables are built automatically the first time the server runs.

## Working with Roles

1. Visit `/createaccount` to register. Pick the appropriate role (Student, TA, Instructor).
2. Use `/login` to access the site. The navigation sidebar adapts to your role.
3. Instructors can publish/delete assignments and announcements from the UI; TAs can view everything, grade submissions, and tweak rubrics but cannot publish/delete assignments.
4. When you’re done, use the **Sign Out** link (or `/logout`) to terminate the session safely.

## Assignment Workflow

### Instructor
1. Ensure at least one course exists (`Courses → Add Course`).
2. Create assignments via `Assignments → New Assignment`.
3. Optionally add more rubric rows inside each assignment detail page.
4. Grade student submissions from the same detail page using the rubric inputs.
5. Use the **Delete Assignment** button (instructors only) on the assignment detail or list pages.

### Student
1. Open `Courses → Manage My Classes` to select which courses should appear on the dashboard.
2. Use the dashboard or assignment list to jump into each assignment.
3. Submit work through the assignment detail page and review rubric results once graded.

## Announcements

- View all announcements at `/announcements`.
- Instructors can post new items at `/announcements/new`, targeting a specific course or the general audience, and remove outdated announcements directly from the list/detail views.

## Courses & Class Selection

- Instructors add course metadata at `/courses/new`.
- All users can browse the catalog via `/courses`.
- Students curate their dashboard classes through `/classes/manage` (multi-select control).

## Data & Environment Notes

- SQLite files (`app/app.db`, `instance/app.db`) are ignored in Git, so you’ll always start with a clean database after cloning.
- Use `python create_db.py` anytime you want to wipe and rebuild tables locally.


## Screenshots

![Home Page Screenshot](screenshots/Dashboard.png)
![Create_Assign](screenshots/create_assign.png)
![Instructor_Annc](screenshots/instr_annc.png)
![manage](screenshots/manage_class.png)
![student](screenshots/student%20class.png)

