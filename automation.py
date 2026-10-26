import os
import smtplib
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2 import service_account
from googleapiclient.discovery import build

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD")
SERVICE_ACCOUNT_FILE = os.environ.get(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "service_account.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_creds():
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )


def send_email(pdf_path: str, summary: dict, recipient_email: str) -> dict:
    """Send PDF report to user via Gmail SMTP."""
    try:
        msg            = MIMEMultipart()
        msg["To"]      = recipient_email
        msg["From"]    = GMAIL_USER
        msg["Subject"] = f"Student Performance Report — Top: {summary['top_student']}"

        body = (
            f"Hi,\n\n"
            f"Your AI-generated student performance report is attached.\n\n"
            f"Summary:\n"
            f"  Overall Average : {summary['overall_average']}\n"
            f"  Top Student     : {summary['top_student']} ({summary['top_score']})\n"
            f"  Weak Subjects   : {', '.join(summary['weak_subjects'].keys()) or 'None'}\n\n"
            f"Best regards,\nAI Report Generator"
        )
        msg.attach(MIMEText(body, "plain"))

        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=report.pdf")
        msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, recipient_email, msg.as_string())

        print(f"EMAIL: sent to {recipient_email}")
        return {"label": f"Email sent to {recipient_email}", "ok": True}

    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        return {"label": f"Email failed: {str(e)}", "ok": False}


def log_to_sheets(summary: dict, job_id: str, sheets_id: str) -> dict:
    """Append a row to user's Google Sheet."""
    try:
        creds   = get_creds()
        service = build("sheets", "v4", credentials=creds)

        row = [[
            job_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary["top_student"],
            summary["top_score"],
            summary["overall_average"],
            ", ".join(summary["weak_subjects"].keys()) or "None",
        ]]

        service.spreadsheets().values().append(
            spreadsheetId=sheets_id,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body={"values": row},
        ).execute()

        print("SHEETS: row logged")
        return {"label": "Logged to Google Sheets", "ok": True}

    except Exception as e:
        print(f"SHEETS ERROR: {e}")
        return {"label": f"Sheets failed: {str(e)}", "ok": False}


def run_automation(
    pdf_path: str,
    summary: dict,
    job_id: str,
    email: str,
    drive_folder: str,   # kept for API compatibility, not used
    sheets_id: str,
) -> list:
    results = []

    if email:
        results.append(send_email(pdf_path, summary, email))

    if sheets_id:
        results.append(log_to_sheets(summary, job_id, sheets_id))

    return results
