# Mini ATS (Applicant Tracking System) — Flask

A simple, official-style job application portal with:
- Applicant form (personal info, education, experience, resume upload)
- SQLite database storage
- Admin dashboard to view applications, download resumes, update status
- Applicant tracking page to check status using Application ID + Email

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5000/

### Admin Login
- URL: `/admin/login`
- Password (default): `admin123`  
  Set your own via env var:

```bash
export ADMIN_PASSWORD="your-strong-password"
export APP_SECRET="your-secret-key"
```

## Project Structure
```
job_form_ats/
│-- app.py
│-- app.db (created on first run)
│-- uploads/            # resumes saved here
│-- templates/
│   ├── base.html
│   ├── job_form.html
│   ├── success.html
│   ├── track.html
│   └── applications.html
│-- static/
│   └── job_form.css
│-- requirements.txt
│-- README.md
```

## Notes
- Allowed resume formats: .pdf, .doc, .docx, .jpg, .jpeg, .png
- Change status options in `applications.html` if needed.
- For production, put behind a proper server and use a real database & storage.
