install:
	cd ./app && pipenv install

dev: install
	cd ./app && pipenv run python main.py
