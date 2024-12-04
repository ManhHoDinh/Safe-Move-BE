FROM python:3.10-slim

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

RUN pip install --no-cache-dir -r /app/requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /app/

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
