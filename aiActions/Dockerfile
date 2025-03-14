FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV HOST = localhost

COPY main.py .
COPY modele.py .
COPY model2.keras .

EXPOSE 8001

CMD ["python3", "main.py"]
