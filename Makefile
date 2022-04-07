deps:
	poetry install

dev: deps
	cd app && poetry run python main.py

lint: lint-black lint-flake lint-pycodestyle

lint-black:
	poetry run black --line-length 100 app

lint-flake:
	poetry run flake8 --max-line-length 100 app

lint-pycodestyle:
	poetry run pycodestyle --max-line-length 100 ./app
