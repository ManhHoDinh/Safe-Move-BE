FROM tiangolo/uvicorn-gunicorn:python3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN apt update && \
    apt install -y htop libgl1-mesa-glx libglib2.0-0


RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]
EXPOSE 8001