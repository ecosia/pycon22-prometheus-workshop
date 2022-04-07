FROM python:3.10.1-slim-buster

RUN pip install poetry

COPY ./pyproject.toml /
COPY ./poetry.lock /
RUN poetry install

COPY ./app /python_server

WORKDIR /python_server
EXPOSE 8001
CMD ["poetry", "run", "python", "main.py"]
