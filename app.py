from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import sqlite3, os, uuid, datetime
from werkzeug.utils import secure_filename

# --- Config ---
APP_SECRET = os.environ.get("APP_SECRET", "change-me-secret")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")  # demo only
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTS = {"pdf", "doc", "docx", "jpg", "jpeg", "png"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = APP_SECRET
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- DB Helpers ---
def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            dob TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            pincode TEXT,
            highest_qualification TEXT,
            university TEXT,
            grad_year TEXT,
            cgpa TEXT,
            experience_years TEXT,
            job_role TEXT,
            skills TEXT,
            github TEXT,
            linkedin TEXT,
            why_you TEXT,
            resume_filename TEXT,
            status TEXT DEFAULT 'Submitted'
        )
    """)
    conn.commit()
    conn.close()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

@app.route("/", methods=["GET", "POST"])
def job_form():
    if request.method == "POST":
        # Read form fields
        f = request.form
        file = request.files.get("cv")

        resume_filename = ""
        if file and file.filename:
            if allowed_file(file.filename):
                safe_name = secure_filename(file.filename)
                # prefix with uuid to avoid collisions
                resume_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_filename))
            else:
                flash("Invalid resume format. Allowed: pdf, doc, docx, jpg, jpeg, png")
                return redirect(url_for("job_form"))

        # Generate application id
        app_id = "JOB-" + uuid.uuid4().hex[:8].upper()

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO applications
            (app_id, first_name, last_name, email, phone, dob, address, city, state, pincode,
             highest_qualification, university, grad_year, cgpa, experience_years, job_role,
             skills, github, linkedin, why_you, resume_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app_id,
            f.get("first_name"), f.get("last_name"), f.get("email"), f.get("phone_no"),
            f.get("date"),
            f.get("address"), f.get("city"), f.get("state"), f.get("pincode"),
            f.get("highest_qualification"), f.get("university"), f.get("grad_year"), f.get("cgpa"),
            f.get("experience_years"), f.get("job_role"),
            f.get("skills"), f.get("github"), f.get("linkedin"), f.get("why_you"),
            resume_filename
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("success", app_id=app_id))

    return render_template("job_form.html")

@app.route("/success/<app_id>")
def success(app_id):
    return render_template("success.html", app_id=app_id)

@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# --- Tracking ---
@app.route("/track", methods=["GET", "POST"])
def track():
    result = None
    if request.method == "POST":
        app_id = request.form.get("app_id")
        email = request.form.get("email")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM applications WHERE app_id=? AND email=?", (app_id, email))
        row = cur.fetchone()
        conn.close()
        result = row
        if not row:
            flash("No application found. Check your Application ID and Email.")
    return render_template("track.html", result=result)

# --- Admin ---
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid password.")
    return render_template("login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

def admin_required():
    return session.get("admin") is True

@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if not admin_required():
        return redirect(url_for("admin_login"))

    # Update status if posted
    if request.method == "POST":
        new_status = request.form.get("status")
        app_id = request.form.get("app_id")
        if new_status and app_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE applications SET status=? WHERE app_id=?", (new_status, app_id))
            conn.commit()
            conn.close()
            flash(f"Status for {app_id} updated to {new_status}.")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM applications ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template("applications.html", applications=rows)

# --- CLI helper to init DB on first run ---
if __name__ == "__main__":
    # Init database before running
    with app.app_context():
        init_db()
    app.run(debug=True)
