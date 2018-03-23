FROM python:3.6
MAINTAINER qiu0130 <qiu159050@gmail.com>
RUN mkdir /app/

COPY usth_api /app/usth_api
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple --no-cache -r /app/requirements.txt
WORKDIR /app/usth_api/