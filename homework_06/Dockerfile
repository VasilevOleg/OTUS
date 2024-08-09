FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip poetry

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false --local

RUN poetry install

COPY ./app/ ./

COPY ./entrypoint.sh ./

RUN chmod +x ./entrypoint.sh

RUN ["./entrypoint.sh"]

CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"]