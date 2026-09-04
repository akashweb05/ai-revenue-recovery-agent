# Revenue Recovery Agent

> AI-powered autonomous revenue recovery for failed payments.

The **Revenue Recovery Agent** detects failed payments, identifies revenue at risk, diagnoses the likely root cause, selects an appropriate recovery intervention, enforces policy controls, executes bounded recovery actions, and verifies whether revenue was successfully recovered.

The project is designed as a **closed-loop AI recovery system** that moves beyond passive payment monitoring and measures actual revenue recovery.

---

## 🏗️ System Architecture

<p align="center">
      <img src="images/architecture.png" alt="AI Revenue Recovery Agent Architecture" width="100%">
</p>

---

## Problem

Payment failures can result in significant revenue loss.

Businesses often know that a payment has failed, but recovering that revenue requires several decisions:

- Why did the payment fail?
- Is the failure temporary or permanent?
- Should the payment be retried?
- Should the customer receive a reminder?
- Should a new payment link be sent?
- Is the action allowed according to business policy?
- Was the payment eventually recovered?

These decisions are often manual, fragmented, and reactive.

The Revenue Recovery Agent automates this workflow.

---

## Solution

The system creates a complete recovery lifecycle:

```text
Failed Payment
      |
Revenue Risk Detection
      |
AI Diagnosis
      |
Recovery Probability
      |
Recommended Intervention
      |
Policy Evaluation
      |
Execution
      |
Payment Verification
      |
Recovered Revenue
```

Instead of simply reporting failed payments, the system takes controlled recovery actions and measures the final outcome.

---

## Architecture

### Recovery Pipeline

1. **Failed Payment** enters the system with amount, payment method, failure details, customer, and merchant information.
2. **Revenue Risk Detection** identifies payments that represent potential revenue loss and creates recovery cases.
3. **AI Diagnosis** analyzes payment failure information and determines the likely root cause.
4. **Recovery Agent** estimates recovery probability and recommends retry, reminder, or payment link interventions.
5. **Policy Engine** allows, blocks, or escalates the recommended action.
6. **Execution Engine** executes approved recovery actions.
7. **Payment Verification** verifies whether the recovery was successful.

This provides bounded automation with stopping controls and a complete audit trail.

---

## Key Features

- AI-powered recovery decisions based on diagnosis and recovery probability.
- Automatic revenue risk detection for failed payments.
- Root cause diagnosis for payment failures.
- Recovery probability estimation and intervention recommendations.
- Policy-controlled automation with allowed, blocked, and escalated outcomes.
- Retry, reminder, and payment link interventions.
- Execution and payment verification.
- Recovered money and recovery rate measurement.
- Complete recovery case lifecycle and timeline.
- Interactive merchant demo simulation.

---

## 📸 Product Screenshots

### 🏠 Revenue Recovery Dashboard

<p align="center">
      <img src="images/dashboard.png" alt="Revenue Recovery Dashboard" width="100%">
</p>

The dashboard provides a portfolio-level overview of revenue at risk, recovered revenue, recovery rate, case status, and intervention distribution.

---

### 🤖 AI Recovery Simulation

<p align="center">
      <img src="images/demo_simulation.png" alt="AI Recovery Simulation" width="100%">
</p>

The Demo Simulation generates a merchant payment cohort and runs the complete recovery pipeline through risk detection, diagnosis, policy evaluation, execution, and verification.

---

### 📋 Recovery Cases

<p align="center">
      <img src="images/recovery_cases.png" alt="Recovery Cases" width="100%">
</p>

Recovery cases provide a searchable and filterable view of payments processed by the agent, including amount at risk, diagnosis, probability, recommended action, policy, execution, and verification results.

---

### 🔍 Case Lifecycle

<p align="center">
      <img src="images/case_detail.png" alt="Recovery Case Detail" width="100%">
</p>

Each recovery case includes payment, customer, diagnosis, recovery, policy, execution, verification, and a dynamically generated lifecycle timeline.

---

## End-to-End Demo

```text
Generate Demo Payments
        |
Identify Failed Payments
        |
Create Revenue Risk Cases
        |
Diagnose Root Cause
        |
Estimate Recovery Probability
        |
Select Intervention
        |
Evaluate Policy
        |
Execute Action
        |
Verify Payment
        |
Calculate Recovered Revenue
```

Example batch output:

```json
{
  "merchant_id": 2,
  "new_risk_cases_detected": 19,
  "cases_processed": 19,
  "actions_executed": 19,
  "actions_blocked": 0,
  "successful_recoveries": 4,
  "total_amount_at_risk": 125000,
  "recovered_amount": 36000,
  "money_recovery_rate": 28.8
}
```

This demonstrates that the system measures actual recovered revenue, not only executed actions.

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL

### Frontend

- React
- Vite
- TypeScript
- Tailwind CSS
- Axios
- Recharts

---

## Project Structure

```text
revenue-recovery-agent
|
|- backend
|  |- app
|  |  |- models
|  |  |- routes
|  |  |- services
|  |  |- database
|  |  |- schemas
|  |  |- execution
|  |  |- policy
|  |  |- agents
|  |  `- main.py
|  `- requirements.txt
|
|- frontend
|  |- src
|  |  |- api
|  |  |- types
|  |  |- App.tsx
|  |  |- main.tsx
|  |  `- styles.css
|  `- package.json
|
|- .gitignore
`- README.md
```

---

## Core API Endpoints

### Payments

```text
POST /api/payments/
```

Creates a payment record.

### Revenue Risk

```text
POST /api/risk/scan
```

Scans payments and identifies revenue at risk.

### AI Diagnosis

```text
POST /api/diagnosis/{risk_case_id}
```

Diagnoses the likely cause of a payment failure.

### Recovery Agent

```text
POST /api/recovery/{risk_case_id}
```

Analyzes recovery probability and recommends an intervention.

### Recovery Orchestrator

```text
POST /api/recovery/process
```

Processes failed payments through the recovery workflow.

### Policy Engine

```text
POST /api/policy/{recovery_id}
```

Evaluates whether the recommended action is allowed.

### Execution Engine

```text
POST /api/execution/{policy_evaluation_id}
```

Executes the approved recovery action.

### Payment Verification

```text
POST /api/verification/{execution_id}
```

Verifies whether the payment was successfully recovered.

### Dashboard

```text
GET /api/dashboard/metrics
GET /api/dashboard/summary
GET /api/dashboard/cases
GET /api/dashboard/cases/{risk_case_id}
GET /api/dashboard/cases/{risk_case_id}/timeline
```

Returns dashboard metrics, summary analytics, recovery cases, case details, and lifecycle timelines.

### Demo Data Generation

```text
POST /api/demo/generate
```

Generates realistic customers and payment data.

### End-to-End Batch Processing

```text
POST /api/batch/process
```

Runs the complete recovery workflow.

---

## Running the Project

### Prerequisites

- Python 3.10+
- Node.js
- PostgreSQL

### Backend Setup

Navigate to the backend:

```powershell
cd backend
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/revenue_recovery
```

Start FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000  
Swagger: http://127.0.0.1:8000/docs

### Frontend Setup

Navigate to the frontend:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
Copy-Item .env.example .env
```

Configure the API URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start Vite:

```powershell
npm run dev
```

Frontend: http://localhost:5173

### Demo Workflow

1. Open http://localhost:5173.
2. Navigate to **Demo Simulation**.
3. Enter the merchant ID, customer count, and payments per customer.
4. Click **Run AI Recovery Agent**.
5. Review cases processed, actions executed, blocked actions, escalations, successful recoveries, revenue at risk, recovered revenue, and recovery rate.

---

## Validation

### Backend

```powershell
cd backend
python -m py_compile app/main.py app/routes/dashboard.py app/services/dashboard_service.py
```

### Frontend

```powershell
cd frontend
npm run build
```

---

## Design Principles

- **Closed-loop recovery:** the workflow continues until the payment outcome is verified.
- **Bounded automation:** recovery actions pass policy controls before execution.
- **Measurable outcomes:** success is measured through recovered revenue.
- **Auditability:** each case contains a lifecycle trail of decisions and actions.
- **Scalable workflow:** merchant-level batch processing supports multiple recovery cases.

---

## Future Improvements

- Real Razorpay payment gateway integration.
- Webhook-based real-time payment failure detection.
- Machine-learning-based recovery probability models.
- LLM-powered diagnosis explanations.
- Customer communication personalization.
- Retry scheduling and advanced policy configuration.
- Merchant authentication and multi-tenant support.
- Real-time event streaming and production deployment.

---

## Why This Matters

Revenue loss rarely happens in one clean step. A payment may fail because of insufficient funds, temporary banking issues, expired payment methods, or other transaction failures.

The Revenue Recovery Agent transforms:

```text
Payment Failed
      |
Manual Investigation
      |
Manual Follow-up
      |
Unknown Outcome
```

into:

```text
Payment Failed
      |
AI Diagnosis
      |
Controlled Recovery Action
      |
Policy Enforcement
      |
Execution
      |
Verification
      |
Measured Revenue Recovery
```

---

## Author

**Akashdeep Singh**

GitHub: [https://github.com/akashweb05](https://github.com/akashweb05)

---

## Project Status

**System Operational**

The project includes a working backend, interactive frontend dashboard, recovery case management, controlled demo simulation, and end-to-end revenue recovery workflow.
