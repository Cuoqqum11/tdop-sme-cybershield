.PHONY: help install-backend up down logs api-local test-api

help:
	@echo "Available commands:"
	@echo "make install-backend"
	@echo "make up"
	@echo "make down"
	@echo "make logs"
	@echo "make api-local"

install-backend:
	cd backend && pip install -r requirements.txt

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

api-local:
	cd backend && uvicorn app.main:app --reload

test-api:
	curl -X GET http://localhost:8000/health