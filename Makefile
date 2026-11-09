.PHONY: test run lint

test:
	pytest

run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
