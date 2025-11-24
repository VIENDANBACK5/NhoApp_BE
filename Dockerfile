FROM python:3.12.3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt update 
RUN apt upgrade -y 
# Thêm Tesseract OCR, PaddleOCR dependencies và Vietnamese language pack
RUN apt install -y nano unixodbc unixodbc-dev \
    tesseract-ocr \
    tesseract-ocr-vie \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod 777 entrypoint.sh

