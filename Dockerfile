FROM python:3.14.0a1-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD ["python3","./app.py"]

