FROM python:3.11-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

WORKDIR /usr/src/myapp/

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["waitress", "--listen=0.0.0.0:8080", "main:app"]