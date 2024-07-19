FROM python:3.11

RUN pip install poetry==1.8.2

WORKDIR /app

COPY . .

RUN poetry install

CMD ["poetry", "run", "python", "-m" ,"main"]