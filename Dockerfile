FROM python:3.12.2-slim as devnet_webservices

COPY ./main.py /app/
COPY ./routers/templates.py ./routers/webhooks.py /app/routers/
COPY ./db/crud.py ./db/database.py ./db/model.py /app/db/
COPY ./utils/webex.py /app/utils/
COPY ./requirements.txt /app
ENV DB_CONNECTION="mongodb+srv://david:05ykxtTHVgg5JiMl@cluster0.jnrozjs.mongodb.net/admin"
ENV BOT_ACCESS_TOKEN="Y2NjNjU1ODItNDAzYi00ZDBmLWEyNzQtMDFmNjExMGRlNjJjODE0ZGE2NjAtNWI3_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0"]
