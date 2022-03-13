deps:
	poetry install

dev: deps
	cd app && poetry run python app/main.py
