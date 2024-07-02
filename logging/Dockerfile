FROM python:3.10-slim

WORKDIR /service/

# COPY requirements.txt ./

# COPY logger-config.json ./

COPY . /service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV NAME World

CMD ["python", "src/main.py"]