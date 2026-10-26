# AI Report Generator

A web-based application that analyzes CSV datasets, generates AI-assisted reports, and creates downloadable PDF summaries.

## Features
- Upload CSV files for analysis.
- Calculate student and subject performance statistics using pandas.
- Generate natural-language reports using Mistral AI.
- Export reports as PDF files.
- Integrate Gmail for email delivery and Google Sheets for logging.

## Tech Stack
Python · FastAPI · pandas · Mistral AI · FPDF · Google Sheets API · Gmail SMTP · HTML · CSS · JavaScript

## Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/negisaatvik3-bit/ai-report-generator.git
cd ai-report-generator
```

**2. Create a virtual environment**
```bash
python -m venv .venv
```

Activate it on Windows:
```powershell
.venv\Scripts\Activate.ps1
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Set up your Mistral API key and, if using the integrations, your Gmail app password and Google service-account credentials. Never commit secrets to GitHub.

**5. Run the application**
```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 in your browser.

## Project Structure
- `main.py` — FastAPI application and endpoints
- `pipeline.py` — Data analysis and PDF report generation
- `automation.py` — Email and Google Sheets integrations
- `dashboard.py` — Streamlit dashboard
- `static/` — Web interface
- `data/` — Sample dataset

## Author
**Saatvik Negi**

[GitHub Repository](https://github.com/negisaatvik3-bit/ai-report-generator)
