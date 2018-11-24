FROM python:3.6.7-alpine3.8
COPY . /app
RUN pip3 install -r /app/requirements.txt