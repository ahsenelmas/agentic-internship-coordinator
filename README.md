# Agentic Internship Coordinator

The **Agentic Internship Coordinator** is an AI-powered internship application processing system built with **FastAPI**, **LangGraph**, **PostgreSQL**, **n8n**, **Streamlit**, and **LangSmith**.

The system receives internship application emails, processes them through a multi-agent workflow, validates application completeness and university rules, stores results in a database, and displays processed cases in a professional dashboard.

The project also includes **LLM observability with LangSmith**, allowing each LangGraph agent step to be traced, inspected, and debugged.

---

## Project Overview

Internship application processing often requires manual checking of student information, company details, supervisor data, internship dates, missing fields, and rule violations.

This project supports and automates that process using an agentic workflow.

The system can:

- Receive internship application data from email automation
- Process application content through a LangGraph workflow
- Extract student, company, supervisor, and internship information
- Validate whether required fields are complete
- Check basic university internship rules
- Generate an agent recommendation
- Store cases and audit logs in PostgreSQL
- Display processed applications in a Streamlit dashboard
- Allow a human coordinator to record the final decision
- Trace workflow execution with LangSmith observability

---

<img width="1917" height="882" alt="image" src="https://github.com/user-attachments/assets/0246e898-2b85-4257-8536-1878dc223192" />


## Tech Stack

### Backend

- Python
- FastAPI
- LangGraph
- SQLAlchemy
- PostgreSQL
- Pydantic

### Frontend

- Streamlit
- Pandas
- Plotly
- Requests

### Database

- Neon PostgreSQL

### Automation

- n8n
- Gmail Trigger
- HTTP Request integration

### Deployment

- Coolify
- Docker
- GitHub

### Observability

- LangSmith
- LangGraph tracing
- Agent workflow inspection

---

## System Architecture

```text
Gmail / Email
    ↓
n8n Workflow
    ↓
FastAPI Backend
    ↓
LangGraph Agent Workflow
    ↓
LangSmith Observability
    ↓
Neon PostgreSQL Database
    ↓
Streamlit Dashboard
    ↓
Coordinator Final Decision
```

---

## Agent Workflow

The backend uses a LangGraph workflow with specialized agents.

```text
Email Intake Agent
    ↓
Document Extraction Agent
    ↓
Completeness Validation Agent
    ↓
University Rules Agent
    ↓
Supervisor Verification Agent
    ↓
Decision Recommendation Agent
```

The workflow can route cases depending on their state. For example, if required fields are missing, the system can skip later steps and directly generate a clarification recommendation.

---

## Main Features

## 1. Email Intake

The system receives internship application data from n8n or direct API requests.

Supported input fields:

- Email sender
- Email subject
- Email body
- Attachment paths

---

## 2. Document and Field Extraction

The system extracts important internship application information, including:

- Student name
- Student ID
- Student email
- Company name
- Supervisor name
- Supervisor email
- Internship start date
- Internship end date

---

## 3. Completeness Validation

The completeness validation agent checks whether required application fields are missing.

If important information is missing, the system can recommend:

```text
REQUEST_CLARIFICATION
```

---

## 4. University Rules Validation

The university rules agent checks whether the internship application follows basic university internship requirements.

For example, it can identify rule violations such as an invalid or too-short internship period.

---

## 5. Supervisor Verification

The supervisor verification step checks whether supervisor-related information is available and usable.

---

## 6. Decision Recommendation

The final recommendation agent produces one of the following outcomes:

```text
APPROVE
REQUEST_CLARIFICATION
REJECT_OR_CLARIFY
```

The recommendation is advisory. The final decision is still recorded by a human coordinator.

---

## 7. Human-in-the-Loop Dashboard

The Streamlit dashboard allows the internship coordinator to:

- View all processed cases
- Inspect extracted application information
- Review agent recommendations
- Check audit logs
- Approve an application
- Reject an application
- Request clarification
- Monitor system status

---

## 8. Audit Logs

Each processed case includes audit logs showing what happened during the workflow.

Example audit events:

```text
Email Intake Agent: Email received
Document Extraction Agent: Extracted application fields
Completeness Validation Agent: Missing fields checked
University Rules Agent: Internship rules validated
Decision Recommendation Agent: Recommendation generated
```

---

## Observability with LangSmith

LangSmith observability was integrated into the backend to trace the LangGraph agent workflow.

Each internship application processing run is traceable in LangSmith, including:

- Input data
- Agent execution order
- Routing decisions
- Intermediate workflow states
- Audit logs
- Final recommendation
- Runtime and latency

This makes the system easier to debug, monitor, and evaluate in a production-style environment.

<img width="1621" height="541" alt="image" src="https://github.com/user-attachments/assets/4e357e4b-b337-4fa4-9e7e-d88e280ec5e6" />

### Example LangSmith Trace

```text
internship_case_intake
    ├── email_intake
    ├── document_extraction
    ├── completeness_validation
    ├── route_after_completeness
    └── decision_recommendation
```

### LangSmith Environment Variables

For production deployment, the backend uses the following environment variables:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=agentic-internship-coordinator
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
APP_ENV=production
```

For local development:

```env
APP_ENV=local
```

---

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

---

### Process Case from JSON Intake

```http
POST /cases/intake
```

Example request:

```json
{
  "email_sender": "student@example.com",
  "email_subject": "Internship Application",
  "email_body": "Student Name: Ayse Yilmaz\nStudent ID: 123456\nCompany Name: ABC Tech\nSupervisor Name: John Smith\nSupervisor Email: john@abctech.com\nInternship Start Date: 2026-07-01\nInternship End Date: 2026-08-15",
  "attachment_paths": []
}
```

---

### Upload PDF Application

```http
POST /cases/upload
```

This endpoint accepts form data and a PDF file.

---

### List All Cases

```http
GET /cases
```

---

### Get Case by ID

```http
GET /cases/{case_id}
```

---

### Get Case Audit Logs

```http
GET /cases/{case_id}/audit-logs
```

---

### Approve Case

```http
POST /cases/{case_id}/approve
```

---

### Reject Case

```http
POST /cases/{case_id}/reject
```

---

### Request Clarification

```http
POST /cases/{case_id}/request-clarification
```

---

## Deployment

The project is deployed using Coolify.

### Backend Deployment

The FastAPI backend is deployed as a Coolify application.

```text
Backend URL:
https://internship-backend.codewithpeter.com
```

Backend internal port:

```text
8000
```

Backend Docker command:

```dockerfile
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

---

### Frontend Deployment

The Streamlit dashboard is deployed as a separate Coolify application.

```text
Dashboard URL:
https://internship-dashboard.codewithpeter.com
```

Frontend internal port:

```text
8501
```

Frontend Docker command:

```dockerfile
CMD ["sh", "-c", "streamlit run dashboard.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
```

---

### Database Deployment

The system uses Neon PostgreSQL as the production database.

Required backend environment variable:

```env
DATABASE_URL=your_neon_database_url
```

---

## n8n Integration

n8n is used to automate the email workflow.

The workflow structure is:

```text
Gmail Trigger
    ↓
HTTP Request to FastAPI Backend
    ↓
Switch Based on Recommendation
    ↓
Send Email Response
```

The n8n HTTP Request node calls the deployed backend endpoint:

```text
https://internship-backend.codewithpeter.com/cases/intake
```

If API key protection is enabled, the request includes:

```text
x-api-key: your_backend_api_key
```

---

## Environment Variables

### Backend

```env
DATABASE_URL=your_neon_database_url
API_KEY=your_backend_api_key
N8N_API_KEY=your_n8n_api_key

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=agentic-internship-coordinator
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
APP_ENV=production
```

### Frontend

```env
BACKEND_URL=https://internship-backend.codewithpeter.com
API_KEY=your_backend_api_key
```

---

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/agentic-internship-coordinator.git
cd agentic-internship-coordinator
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend
pip install -r requirements.txt
streamlit run dashboard.py
```

---

## Testing

The backend includes automated tests using `pytest`.

The tests cover:

- FastAPI health endpoint
- Case listing API
- LangGraph agent decision workflow
- Invalid input handling
- Case decision actions

Run tests from the backend folder:

```bash
cd backend
python -m pytest
```

Example successful result:

```text
3 passed, 1 warning
```

Testing was performed through:

- Local pytest test suite
- Deployed backend health check
- Swagger API testing
- Neon database verification
- Streamlit dashboard validation
- n8n workflow testing
- LangSmith trace verification

---

## Example End-to-End Test Flow

A complete system test follows this flow:

```text
1. Send internship application email
2. n8n receives the email
3. n8n sends application data to FastAPI
4. FastAPI runs the LangGraph workflow
5. LangSmith records the trace
6. Neon PostgreSQL stores the case
7. Streamlit dashboard displays the case
8. Coordinator records final decision
9. n8n sends response email
```

---

## Project Status

Completed features:

- FastAPI backend
- LangGraph agent workflow
- PostgreSQL database integration
- Neon deployment
- Coolify backend deployment
- Coolify Streamlit dashboard deployment
- n8n email workflow integration
- Human-in-the-loop dashboard
- Automated backend tests
- LangSmith observability integration

---

## Future Improvements

Possible next steps:

- Add authentication to the Streamlit dashboard
- Add role-based access control for coordinators
- Improve PDF document extraction
- Add configurable university internship rules
- Add more evaluation metrics for agent recommendations
- Add LangSmith datasets and evaluators
- Add monitoring alerts for failed workflow executions
- Improve production security and logging
