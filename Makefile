.PHONY: install test serve frontend

install:
	pip install -r requirements.txt

test:
	pytest

serve:
	uvicorn main:app --reload --port 8000

frontend:
	python -m http.server --directory frontend 8001
