FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY config ./config
COPY apps ./apps
COPY manage.py ./

RUN pip install --upgrade pip && pip install .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
