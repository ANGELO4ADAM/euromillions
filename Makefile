.PHONY: install test serve frontend preview pages

install:
	 pip install -r requirements.txt

test:
	 pytest

serve:
	 uvicorn main:app --reload --port 8000

frontend:
	 python -m http.server --directory frontend 8001

preview:
	 python -m http.server --directory frontend 8000

pages:
	 rm -rf docs
	 mkdir -p docs
	 cp -r frontend/* docs/
