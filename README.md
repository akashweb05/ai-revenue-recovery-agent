# Revenue Recovery Agent

AI-powered revenue risk detection and recovery orchestration for failed payments.

## Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React, Vite, TypeScript, Tailwind CSS, Axios, Recharts

## Run the backend

1. Start PostgreSQL and make sure the connection string in `backend/.env` is valid:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/revenue_recovery
```

2. Install backend dependencies and start FastAPI:

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000  
Swagger: http://127.0.0.1:8000/docs

## Run the frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend: http://localhost:5173

The frontend reads `VITE_API_BASE_URL` from `frontend/.env`. The default is `http://127.0.0.1:8000`.

## Main API endpoints

- `GET /api/dashboard/metrics`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/cases`
- `GET /api/dashboard/cases/{risk_case_id}`
- `GET /api/dashboard/cases/{risk_case_id}/timeline`
- `POST /api/demo/generate`
- `POST /api/batch/process`

## Frontend pages

- Dashboard: portfolio KPIs, recovery performance, case status, intervention mix
- Recovery cases: searchable and filterable case table
- Case detail: payment, customer, diagnosis, policy, execution, verification, and lifecycle timeline
- Demo simulation: generate data and run the end-to-end recovery agent

## Validation

```powershell
cd backend
python -m py_compile app/main.py app/routes/dashboard.py app/services/dashboard_service.py

cd ..\frontend
npm run build
```
