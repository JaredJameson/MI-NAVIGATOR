.PHONY: run dev test

run:
	./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	./venv/bin/pytest
