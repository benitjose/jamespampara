# Python Flask Intelligence Assessment Web App

This starter project implements a Flask-based web application for an intelligence assessment questionnaire. Users enter their details once and answer section-based questions with values from 1 to 5. After completion, they can view their answers.

## Features

- Introduction page with user details form
- Eight intelligence sections with 7 questions each
- Answers stored in SQLite with user details
- Users can only submit once per email
- Admin dashboard to view all user answers
- Progress tracking and summaries

## Run locally

1. Open a terminal in `C:\Users\benit\python-flask-webapp`
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the app:
   ```powershell
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

## Admin login

Default admin credentials:

- Email: `admin@example.com`
- Password: `Admin123!`

## User Flow

- Enter name and email on the home page
- Complete all 8 sections
- View answers in profile
- Assessment is complete after all sections
