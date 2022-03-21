deps:
	poetry install

dev: deps
	cd app && poetry run python main.py
