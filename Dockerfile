FROM python:3.12.4-alpine

WORKDIR /mtg-helper

COPY ./requirements.txt /mtg-helper/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /mtg-helper/requirements.txt

COPY ./app /mtg-helper/app

RUN cd /mtg-helper/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
