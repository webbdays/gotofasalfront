FROM python:3.11.0-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD ["python3","./app.py"]

