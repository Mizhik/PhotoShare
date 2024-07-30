# Інструкції по запуску 

## Установка 
* Створіть віртуальне середовище: 

```bash
 pip install poetry
```
* Встановіть всі залежності:

```bash
poetry install
```

* Активуйте віртуальне середовище:

```bash
poetry shell
```


## Запуск застосунку 
* Запустіть застосунок за допомогою Uvicorn:
```bash
uvicorn app.main:app --reload
```
*Відкрийте браузер і перейдіть за адресою http://localhost:8000/ для перевірки роботи застосунку.*

## Запуск програми у Docker

Цей проект можна запустити у Docker-контейнері для забезпечення консистентного середовища та простоти розгортання. Нижче наведено кроки для створення та запуску Docker-контейнера.

## Вимоги
Встановлений Docker на вашому комп'ютері. Інструкції щодо встановлення Docker можна знайти на офіційному сайті [Docker](https://docs.docker.com/engine/install/).

## Запуск через Docker Compose
Для запуску додатка разом з PostgreSQL використовуйте Docker Compose.

## Конфігурація Docker Compose
Для запуску Docker Compose використвуйте файл docker-compose.yml та налаштування змінних для баз даних знаходяться у файлі **.env.sample**

* Побудова та запуск Docker-контейнера
```bash
docker-compose up -d --build
```

## Міграції

Створення та застосування міграцій

* Створення міграцій

```bash
alembic revision --autogenerate -m "Опис міграції"
```
* Застосування міграцій

```bash
alembic upgrade head
```

## Для додавання нового типа до бази даних
У файлі міграцій додайте 
```bash
def upgrade():
op.execute('CREATE TYPE as ENUM("admin","moderator","user",)')
...

def downgrade():
...
op.execute("DROP TYPE role")