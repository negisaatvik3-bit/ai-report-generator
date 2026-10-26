# AI Report Generator

An AI-powered student performance reporting application that analyzes CSV datasets, calculates student and subject statistics, generates natural-language reports, and exports them as downloadable PDF documents.

## Overview

The AI Report Generator automates the process of analyzing student marks and preparing performance reports. It combines Python-based data analysis with a Large Language Model (LLM) to turn numerical results into readable summaries.

## Features

- **CSV Data Processing:** Upload student marks using a CSV file.
- **Performance Analytics:** Calculate student averages, subject averages, overall class average, and top-performing students.
- **AI-Generated Reports:** Use the Mistral AI API to generate natural-language performance summaries.
- **PDF Export:** Generate downloadable reports using FPDF.
- **Email Automation:** Support report delivery through Gmail SMTP.
- **Google Sheets Integration:** Log report summaries using the Google Sheets API.
- **Analytics Dashboard:** Explore student performance through a separate Streamlit dashboard with interactive visualizations.

*Note: External integrations require appropriate configuration and credentials. AI report generation depends on an active Mistral API account.*

## Tech Stack

| Component | Technologies |
|---|---|
| Language | Python |
| Backend | FastAPI, Uvicorn |
| Data Analysis | pandas |
| AI | Mistral AI API |
| PDF Generation | FPDF |
| Email | Gmail SMTP |
| Logging | Google Sheets API v4 |
| Frontend | HTML, CSS, JavaScript |
| Dashboard | Streamlit, Plotly |

## Architecture

1. Upload a CSV file through the web interface.
2. FastAPI receives the file and initiates processing.
3. pandas calculates student and subject performance statistics.
4. The Mistral AI API generates a written performance summary.
5. FPDF converts the report into a PDF document.
6. The application provides a report download link and can optionally send the report by email and log summary details to Google Sheets.

## Project Structure

```text
ai-report-generator/
├── main.py
├── pipeline.py
├── automation.py
├── dashboard.py
├── requirements.txt
├── requirements copy.txt
├── ai_report_generator_docs.docx
├── data/
│   └── students
