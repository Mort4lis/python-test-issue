FROM python:3.8
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app/
WORKDIR /app/

EXPOSE 8080

CMD ["python", "./shop/main.py"]
