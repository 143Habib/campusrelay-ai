PYTHON ?= python
.PHONY: install run test evaluate verify
install:
	$(PYTHON) -m pip install -r requirements-dev.txt
run:
	$(PYTHON) -m uvicorn app.main:app --reload --port 8000

test:
	$(PYTHON) -m pytest -q

evaluate:
	$(PYTHON) scripts/evaluate_model.py

verify: test evaluate
	$(PYTHON) scripts/smoke_test.py
