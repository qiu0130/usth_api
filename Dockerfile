FROM python:3.6
MAINTAINER qiu159050@gmail.com
RUN mkdir /app
RUN mdkir /log
ADD . /app
WORKDIR /app/usth_api/
COPY requirements.txt /app/
RUN pip install --no-cache -r requirements.txt
