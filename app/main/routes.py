from datetime import datetime
from flask import render_template, redirect, flash, request, url_for
from flask_login import login_required, current_user

from . import bp
from app import db
from app.models import (
    Classes,
    Course,
    Assignment,
    Submission,
    Announcement,
    RubricCriterion,
)
from app.forms import (
    AssignmentForm,
    AnnouncementForm,
    SubmissionForm,
    RubricCriterionForm,
    CourseForm,
    ClassSelectionForm,
)


def _course_choices(include_general=True):
    courses = Course.query.order_by(Course.course_name).all()
    choices = []
    if include_general:
        choices.append((0, "General / All Courses"))
    choices.extend((course.id, course.course_name) for course in courses)
    return choices


def _selected_course_ids(user_id):
    classes_record = Classes.query.filter_by(user=user_id).first()
    if not classes_record or not classes_record.classes:
        return []
    selected = []
    for entry in classes_record.classes:
        if isinstance(entry, int):
            selected.append(entry)
        elif isinstance(entry, str) and entry.isdigit():
            selected.append(int(entry))
        elif isinstance(entry, dict) and "course_id" in entry:
            selected.append(entry["course_id"])
    return selected


def _build_class_cards(user_id):
    classes_record = Classes.query.filter_by(user=user_id).first()
    if not classes_record or not classes_record.classes:
        return []

    cards = []
    for entry in classes_record.classes:
        if isinstance(entry, dict) and entry.get("title"):
            link = entry.get("link")
            cards.append(
                {
                    "title": entry.get("title"),
                    "course_code": entry.get("course_code", ""),
                    "description": entry.get("description", ""),
                    "link": link,
                }
            )
        else:
            course_id = None
            if isinstance(entry, int):
                course_id = entry
            elif isinstance(entry, str) and entry.isdigit():
                course_id = int(entry)
            elif isinstance(entry, dict) and entry.get("id"):
                course_id = entry["id"]

            if course_id:
                course = Course.query.get(course_id)
                if course:
                    cards.append(
                        {
                            "title": course.course_name,
                            "course_code": course.course_code,
                            "description": course.description or "",
                            "link": url_for("main.course_detail", course_id=course.id),
                        }
                    )
    return cards


def _assignment_badge(assignment, submission=None):
    now = datetime.utcnow()
    if not assignment.allow_submissions:
        return {"label": "Closed", "class": "bg-gray-100 text-gray-700"}
    if submission and submission.status == "Graded":
        return {"label": "Graded", "class": "bg-green-100 text-green-700"}
    if submission:
        return {"label": "Submitted", "class": "bg-blue-100 text-blue-700"}
    if assignment.due_date < now:
        return {"label": "Overdue", "class": "bg-red-100 text-red-700"}
    return {"label": "Pending", "class": "bg-yellow-100 text-yellow-700"}


def _has_role(user, *roles):
    return user.is_authenticated and user.role in roles


def _require_roles(*roles):
    if not _has_role(current_user, *roles):
        flash("You do not have permission to perform this action.", "error")
        return False
    return True


@bp.route("/")
@bp.route("/home")
@login_required
def home():
    assignments = Assignment.query.order_by(Assignment.due_date.asc()).limit(5).all()
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()

    submissions = {}
    if current_user.role == "student":
        user_submissions = Submission.query.filter_by(student_id=current_user.id).all()
        submissions = {sub.assignment_id: sub for sub in user_submissions}

    for assignment in assignments:
        assignment.progress_badge = _assignment_badge(
            assignment, submissions.get(assignment.id)
        )

    classes_payload = _build_class_cards(current_user.id)
    return render_template(
        'home.html',
        classes=classes_payload,
        assignments=assignments,
        announcements=announcements,
    )


@bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role in ["instructor", "ta"]:
        assignments = Assignment.query.filter_by(created_by=current_user.id).order_by(Assignment.due_date).all()
        pending_submissions = Submission.query.join(Assignment).filter(
            Assignment.created_by == current_user.id,
            Submission.status != "Graded",
        ).all()
        return render_template(
            "dashboard.html",
            mode="instructor",
            assignments=assignments,
            pending_submissions=pending_submissions,
        )
    else:
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
        submissions = Submission.query.filter_by(student_id=current_user.id).all()
        submission_map = {s.assignment_id: s for s in submissions}
        for assignment in assignments:
            assignment.progress_badge = _assignment_badge(
                assignment, submission_map.get(assignment.id)
            )
            assignment.submission = submission_map.get(assignment.id)
        return render_template(
            "dashboard.html",
            mode="student",
            assignments=assignments,
        )


@bp.route("/assignments")
@login_required
def assignment_list():
    assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
    submission_map = {}
    if current_user.role == "student":
        submission_map = {
            s.assignment_id: s
            for s in Submission.query.filter_by(student_id=current_user.id).all()
        }
    for assignment in assignments:
        assignment.progress_badge = _assignment_badge(
            assignment, submission_map.get(assignment.id)
        )
    return render_template("assignments_list.html", assignments=assignments)


@bp.route("/courses")
@login_required
def courses():
    all_courses = Course.query.order_by(Course.course_name.asc()).all()
    selected_ids = set(_selected_course_ids(current_user.id))
    return render_template(
        "courses.html",
        courses=all_courses,
        selected_ids=selected_ids,
    )


@bp.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    assignments = Assignment.query.filter_by(course_id=course.id).order_by(Assignment.due_date.asc()).all()
    announcements = Announcement.query.filter_by(course_id=course.id).order_by(Announcement.created_at.desc()).all()

    submission_map = {}
    if current_user.role == "student":
        submission_map = {
            s.assignment_id: s
            for s in Submission.query.filter_by(student_id=current_user.id).all()
        }
    for assignment in assignments:
        assignment.progress_badge = _assignment_badge(
            assignment, submission_map.get(assignment.id)
        )

    return render_template(
        "course_detail.html",
        course=course,
        assignments=assignments,
        announcements=announcements,
    )


@bp.route("/courses/new", methods=["GET", "POST"])
@login_required
def course_create():
    if not _require_roles("instructor"):
        return redirect(url_for("main.courses"))

    form = CourseForm()
    if form.validate_on_submit():
        duplicate = Course.query.filter(
            (Course.course_code == form.course_code.data)
            | (Course.course_name == form.course_name.data)
        ).first()
        if duplicate:
            flash("Course with that name or code already exists.", "error")
        else:
            course = Course(
                course_name=form.course_name.data,
                course_code=form.course_code.data,
                description=form.description.data,
            )
            db.session.add(course)
            db.session.commit()
            flash("Course created successfully.", "success")
            return redirect(url_for("main.courses"))

    return render_template("course_form.html", form=form)


@bp.route("/classes/manage", methods=["GET", "POST"])
@login_required
def manage_classes():
    form = ClassSelectionForm()
    course_choices = _course_choices(include_general=False)
    if not course_choices:
        flash("No courses available yet. Please ask an instructor to add one.", "error")
        return redirect(url_for("main.courses"))

    form.courses.choices = course_choices
    current_selection = _selected_course_ids(current_user.id)
    if request.method == "GET":
        form.courses.data = current_selection

    if form.validate_on_submit():
        selection = form.courses.data or []
        record = Classes.query.filter_by(user=current_user.id).first()
        if not record:
            record = Classes(user=current_user.id, classes=selection)
            db.session.add(record)
        else:
            record.classes = selection
        db.session.commit()
        flash("Classes updated.", "success")
        return redirect(url_for("main.home"))

    courses = Course.query.filter(Course.id.in_([c[0] for c in course_choices])).order_by(Course.course_name).all()
    return render_template("classes_manage.html", form=form, courses=courses)


@bp.route("/assignments/new", methods=["GET", "POST"])
@login_required
def assignment_create():
    if not _require_roles("instructor"):
        return redirect(url_for("main.home"))

    form = AssignmentForm()
    form.course.choices = _course_choices()

    if form.validate_on_submit():
        course_id = form.course.data or None
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            points=form.points.data,
            allow_submissions=form.allow_submissions.data,
            course_id=course_id,
            created_by=current_user.id,
        )
        db.session.add(assignment)
        db.session.flush()

        # seed a simple rubric criterion covering the total points
        criterion = RubricCriterion(
            assignment_id=assignment.id,
            title="Overall Quality",
            description="Default rubric criterion",
            max_points=form.points.data,
        )
        db.session.add(criterion)
        db.session.commit()

        flash("Assignment created successfully.", "success")
        return redirect(url_for("main.assignment_detail", assignment_id=assignment.id))

    return render_template("assignment_form.html", form=form)


@bp.route("/assignments/<int:assignment_id>", methods=["GET", "POST"])
@login_required
def assignment_detail(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    submission_form = SubmissionForm()
    rubric_form = RubricCriterionForm()
    rubric_form.assignment_id.data = assignment.id

    submission = None
    if current_user.role == "student":
        submission = Submission.query.filter_by(
            assignment_id=assignment.id, student_id=current_user.id
        ).first()
        if submission and submission.rubric_scores:
            submission.rubric_scores = {
                int(k): v for k, v in submission.rubric_scores.items()
            }

    if submission_form.validate_on_submit() and current_user.role == "student":
        if not assignment.allow_submissions:
            flash("Submissions are closed for this assignment.", "error")
        else:
            if submission:
                submission.content = submission_form.content.data
                submission.submitted_at = datetime.utcnow()
                submission.status = "Submitted"
            else:
                submission = Submission(
                    assignment_id=assignment.id,
                    student_id=current_user.id,
                    content=submission_form.content.data,
                    status="Submitted",
                )
                db.session.add(submission)
            db.session.commit()
            flash("Submission saved.", "success")
        return redirect(url_for("main.assignment_detail", assignment_id=assignment.id))

    if rubric_form.validate_on_submit() and current_user.role in ["instructor", "ta"]:
        criterion = RubricCriterion(
            assignment_id=assignment.id,
            title=rubric_form.title.data,
            description=rubric_form.description.data,
            max_points=rubric_form.max_points.data,
        )
        db.session.add(criterion)
        db.session.commit()
        flash("Rubric criterion added.", "success")
        return redirect(url_for("main.assignment_detail", assignment_id=assignment.id))

    if submission:
        submission_form.content.data = submission.content

    submissions = []
    if current_user.role in ["instructor", "ta"]:
        submissions = Submission.query.filter_by(assignment_id=assignment.id).all()
        for sub in submissions:
            if sub.rubric_scores:
                sub.rubric_scores = {int(k): v for k, v in sub.rubric_scores.items()}

    return render_template(
        "assignment_detail.html",
        assignment=assignment,
        submission_form=submission_form,
        rubric_form=rubric_form,
        submission=submission,
        submissions=submissions,
    )


@bp.route("/assignments/<int:assignment_id>/grade", methods=["POST"])
@login_required
def grade_submission(assignment_id):
    if not _require_roles("instructor", "ta"):
        return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))

    submission_id = request.form.get("submission_id")
    submission = Submission.query.filter_by(
        id=submission_id, assignment_id=assignment_id
    ).first_or_404()

    rubric_scores = {}
    total = 0
    for criterion in submission.assignment.rubric_criteria:
        field_name = f"criterion_{criterion.id}"
        score_val = request.form.get(field_name, type=int)
        if score_val is None or score_val < 0 or score_val > criterion.max_points:
            flash(f"Invalid points for {criterion.title}.", "error")
            return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))
        rubric_scores[str(criterion.id)] = score_val
        total += score_val

    submission.score = total
    submission.rubric_scores = rubric_scores
    submission.status = "Graded"
    submission.submitted_at = submission.submitted_at or datetime.utcnow()
    db.session.commit()
    flash("Submission graded successfully.", "success")
    return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))

@bp.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
@login_required
def assignment_delete(assignment_id):
    if not _require_roles("instructor"):
        return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))

    assignment = Assignment.query.get_or_404(assignment_id)
    Submission.query.filter_by(assignment_id=assignment.id).delete()
    RubricCriterion.query.filter_by(assignment_id=assignment.id).delete()
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("main.assignment_list"))


@bp.route("/announcements", methods=["GET"])
@login_required
def announcements():
    notes = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("announcements.html", announcements=notes)


@bp.route("/announcements/<int:announcement_id>")
@login_required
def announcement_detail(announcement_id):
    note = Announcement.query.get_or_404(announcement_id)
    return render_template("announcement_detail.html", announcement=note)


@bp.route("/announcements/new", methods=["GET", "POST"])
@login_required
def announcement_create():
    if not _require_roles("instructor"):
        return redirect(url_for("main.announcements"))

    form = AnnouncementForm()
    form.course.choices = _course_choices()

    if form.validate_on_submit():
        course_id = form.course.data or None
        note = Announcement(
            title=form.title.data,
            body=form.body.data,
            course_id=course_id,
            created_by=current_user.id,
        )
        db.session.add(note)
        db.session.commit()
        flash("Announcement published.", "success")
        return redirect(url_for("main.announcements"))

    return render_template("announcement_form.html", form=form)


@bp.route("/announcements/<int:announcement_id>/delete", methods=["POST"])
@login_required
def announcement_delete(announcement_id):
    if not _require_roles("instructor"):
        return redirect(url_for("main.announcements"))

    note = Announcement.query.get_or_404(announcement_id)
    db.session.delete(note)
    db.session.commit()
    flash("Announcement deleted.", "success")
    return redirect(url_for("main.announcements"))

@bp.route("/study-plan", methods=["GET", "POST"])
@login_required
def study_plan():
    from app.main.gpt_client import ask_chatgpt

    advice = None
    if request.method == "POST":
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
        assignmentPrompt = ""
        for assignment in assignments:
            submitted = Submission.query.filter_by(
                assignment_id=assignment.id,
                student_id=current_user.id
            ).first()
            if not submitted:
                assignmentPrompt += f"- {assignment.title}, due {assignment.due_date.strftime('%Y-%m-%d')}({assignment.points} points)\n"
        question = request.form.get("topics", "").strip()
        
        advice = ask_chatgpt(question, assignmentPrompt)
        return render_template("study_plan.html", advice=advice, prefill=question)
       
    return render_template("study_plan.html", advice=advice, prefill="")
