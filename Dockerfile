FROM python:3.12.2-slim as webservices

COPY ./main.py ./favicon.ico /app/
COPY ./routers/templates.py ./routers/webhooks.py /app/routers/
COPY ./db/crud.py ./db/database.py ./db/model.py /app/db/
COPY ./utils/webex.py ./utils/member.py ./utils/session.py /app/utils/
COPY ./requirements.txt /app

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0"]
