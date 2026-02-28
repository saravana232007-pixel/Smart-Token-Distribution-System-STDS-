import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
import csv
import io
from dotenv import load_dotenv
from models import db, Student

load_dotenv()

app = Flask(__name__)

# ── Security ────────────────────────────────────────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", "fallback-dev-key-change-me")

# ── Database ─────────────────────────────────────────────────────────────────
database_url = os.environ.get("DATABASE_URL", "")

if database_url:
    # Render sometimes provides postgres:// — SQLAlchemy needs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(basedir, "ai_medx.db")
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ── Admin credentials ────────────────────────────────────────────────────────
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


# ── Helper ────────────────────────────────────────────────────────────────────
def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════════════


# ── Splash ────────────────────────────────────────────────────────────────────
@app.route("/splash")
def splash():
    return render_template("splash.html")


# ── Student login ─────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        dept = request.form.get("dept", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not dept or not phone:
            return render_template("login.html", error="All fields are required.")

        student = Student.query.filter_by(phone=phone).first()

        if student:
            # Verify name roughly matches (case-insensitive)
            if student.name.lower() == name.lower() and student.dept.lower() == dept.lower():
                return render_template(
                    "result.html",
                    student=student,
                    found=True,
                )
            else:
                return render_template(
                    "result.html",
                    found=False,
                    message="Student details do not match our records.",
                )
        else:
            return render_template("result.html", found=False, message="Student not found.")

    return render_template("login.html")


# ── Admin login ───────────────────────────────────────────────────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials.")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


# ── Admin dashboard ──────────────────────────────────────────────────────────
@app.route("/admin")
@admin_required
def admin_dashboard():
    query = request.args.get("q", "").strip()
    if query:
        students = Student.query.filter(
            (Student.name.ilike(f"%{query}%")) | (Student.phone.ilike(f"%{query}%"))
        ).all()
    else:
        students = Student.query.all()

    total = Student.query.count()
    return render_template(
        "admin_dashboard.html",
        students=students,
        total=total,
        query=query,
    )


# ── Add student ───────────────────────────────────────────────────────────────
@app.route("/admin/upload_csv", methods=["POST"])
@admin_required
def admin_upload_csv():
    if "csv_file" not in request.files:
        flash("No file part provided.", "error")
        return redirect(url_for("admin_dashboard"))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("No selected file.", "error")
        return redirect(url_for("admin_dashboard"))

    if not file.filename.endswith(".csv"):
        flash("Invalid file type. Please upload a .csv file.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)

        success_count = 0
        skipped_count = 0

        for row in csv_input:
            name = row.get("name", "").strip()
            dept = row.get("dept", "").strip()
            phone = row.get("phone", "").strip()
            token = row.get("token", "").strip()

            if not all([name, dept, phone, token]):
                skipped_count += 1
                continue

            if len(token) != 6 or not token.isdigit():
                skipped_count += 1
                continue

            # Check phone uniqueness
            existing_phone = Student.query.filter_by(phone=phone).first()
            if existing_phone:
                skipped_count += 1
                continue

            # Check token uniqueness just to be safe (if token shouldn't have been duplicated as per prompt)
            # Actually, token already exists -> skip row
            existing_token = Student.query.filter_by(token=token).first()
            if existing_token:
                skipped_count += 1
                continue

            student = Student(name=name, dept=dept, phone=phone, token=token)
            db.session.add(student)
            success_count += 1

        db.session.commit()

        if success_count > 0:
            flash(f"Successfully added {success_count} students.", "success")
        if skipped_count > 0:
            flash(f"Skipped {skipped_count} rows (duplicates or invalid data).", "warning")

    except Exception as e:
        db.session.rollback()
        flash("Error processing CSV file. Ensure the format is right.", "error")

    return redirect(url_for("admin_dashboard"))


# ── Add student ───────────────────────────────────────────────────────────────
@app.route("/admin/add", methods=["POST"])
@admin_required
def admin_add():
    name = request.form.get("name", "").strip()
    dept = request.form.get("dept", "").strip()
    phone = request.form.get("phone", "").strip()
    token = request.form.get("token", "").strip()

    if not all([name, dept, phone, token]):
        flash("All fields are required.", "error")
        return redirect(url_for("admin_dashboard"))

    if len(token) != 6 or not token.isdigit():
        flash("Token must be exactly 6 digits.", "error")
        return redirect(url_for("admin_dashboard"))

    existing = Student.query.filter_by(phone=phone).first()
    if existing:
        flash("A student with that phone number already exists.", "error")
        return redirect(url_for("admin_dashboard"))

    student = Student(name=name, dept=dept, phone=phone, token=token)
    db.session.add(student)
    try:
        db.session.commit()
        flash(f"Student '{name}' added successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("Database error while adding student.", "error")

    return redirect(url_for("admin_dashboard"))


# ── Edit student ──────────────────────────────────────────────────────────────
@app.route("/admin/edit/<int:student_id>", methods=["GET", "POST"])
@admin_required
def admin_edit(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        dept = request.form.get("dept", "").strip()
        phone = request.form.get("phone", "").strip()
        token = request.form.get("token", "").strip()

        if not all([name, dept, phone, token]):
            flash("All fields are required.", "error")
            return render_template("admin_edit.html", student=student)

        if len(token) != 6 or not token.isdigit():
            flash("Token must be exactly 6 digits.", "error")
            return render_template("admin_edit.html", student=student)

        # Check phone uniqueness (exclude self)
        conflict = Student.query.filter(
            Student.phone == phone, Student.id != student_id
        ).first()
        if conflict:
            flash("Another student already has that phone number.", "error")
            return render_template("admin_edit.html", student=student)

        student.name = name
        student.dept = dept
        student.phone = phone
        student.token = token

        try:
            db.session.commit()
            flash(f"Student '{name}' updated successfully.", "success")
        except Exception:
            db.session.rollback()
            flash("Database error while updating student.", "error")

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_edit.html", student=student)


# ── Delete student ────────────────────────────────────────────────────────────
@app.route("/admin/delete/<int:student_id>", methods=["POST"])
@admin_required
def admin_delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    try:
        db.session.commit()
        flash(f"Student '{student.name}' deleted.", "success")
    except Exception:
        db.session.rollback()
        flash("Database error while deleting student.", "error")

    return redirect(url_for("admin_dashboard"))


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=False)
