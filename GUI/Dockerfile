FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .
COPY initPages.py .
COPY auxFunctions.py .
COPY aiModel.py .
COPY dataBase.py .


EXPOSE 8501

CMD ["streamlit", "run" , "main.py"]
