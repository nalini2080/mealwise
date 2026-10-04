.PHONY: setup db seed api web test

setup:            ## Install backend + frontend dependencies
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
	cd frontend && npm install

db:               ## Start Postgres in Docker
	docker compose up -d --wait

seed: db          ## (Re)create schema and load seed data
	cd backend && .venv/bin/python -m app.init_db

api:              ## Run the API on :8010 with auto-reload
	cd backend && .venv/bin/uvicorn app.main:app --port 8010 --reload

web:              ## Run the frontend on :5173
	cd frontend && npm run dev

test: db          ## Run backend tests (uses a separate test database)
	cd backend && .venv/bin/pytest -q
