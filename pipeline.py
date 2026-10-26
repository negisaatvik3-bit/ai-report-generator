import os
import pandas as pd
from fpdf import FPDF
from mistralai import Mistral


def run_pipeline(csv_path: str, pdf_path: str) -> dict:
    """Full pipeline: CSV → analysis → Mistral → PDF. Returns summary dict."""

    # ── 1. LOAD & ANALYSE ──────────────────────────────────────────────────
    df = pd.read_csv(csv_path)

    student_avg = df.groupby("Student")["Marks"].mean()
    subject_avg = df.groupby("Subject")["Marks"].mean()

    top_student  = student_avg.idxmax()
    top_score    = student_avg.max()
    overall_avg  = df["Marks"].mean()
    weak_subjects = subject_avg[subject_avg < overall_avg]

    summary = {
        "overall_average":   float(round(overall_avg, 2)),
        "top_student":       top_student,
        "top_score":         float(round(top_score, 2)),
        "student_averages":  {k: float(v) for k, v in student_avg.round(2).to_dict().items()},
        "subject_averages":  {k: float(v) for k, v in subject_avg.round(2).to_dict().items()},
        "weak_subjects":     {k: float(v) for k, v in weak_subjects.round(2).to_dict().items()},
    }

    # ── 2. BUILD PROMPT ────────────────────────────────────────────────────
    prompt = build_ai_prompt(summary)

    # ── 3. CALL MISTRAL ────────────────────────────────────────────────────
    ai_text = get_ai_report(prompt)

    # ── 4. GENERATE PDF ────────────────────────────────────────────────────
    generate_pdf_report(ai_text, pdf_path)

    return summary


# ── HELPERS ────────────────────────────────────────────────────────────────

def build_ai_prompt(summary: dict) -> str:
    return f"""
You are an academic report assistant.

Using the data below, write a clear, professional performance summary
in simple English. Do NOT mention raw data formats or dictionaries.

DATA:
Overall Average Marks: {summary['overall_average']}
Top Student: {summary['top_student']} with {summary['top_score']} marks

Average Marks per Student:
{summary['student_averages']}

Average Marks per Subject:
{summary['subject_averages']}

Subjects Needing Improvement (below overall average):
{summary['weak_subjects']}

Guidelines:
- Write 1–2 short paragraphs
- Use neutral, professional tone
- Highlight top performer
- Mention weak subjects if any
"""


def get_ai_report(prompt: str) -> str:
   api_key = os.environ.get("MISTRAL_API_KEY")
   if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is not configured")
   client = Mistral(api_key=api_key)

   response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": "You are a professional academic report writer."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.4
    )
   return response.choices[0].message.content


def generate_pdf_report(ai_text: str, pdf_path: str) -> None:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Student Performance Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, ai_text)

    pdf.output(pdf_path)


# ── LOCAL TEST (optional) ───────────────────────────────────────────────────
if __name__ == "__main__":
    summary = run_pipeline("data/students_marks.csv", "student_performance_report.pdf")
    print(summary)
