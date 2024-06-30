FROM python:3.12.4-alpine

WORKDIR /mtg-helper

COPY ./requirements.txt /mtg-helper/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /mtg-helper/requirements.txt

COPY ./app /mtg-helper/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
