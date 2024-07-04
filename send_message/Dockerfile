FROM python:3.10-alpine


WORKDIR /send_message

COPY send_message.py /send_message/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir paho-mqtt requests datetime

CMD [ "python", "-u", "./send_message.py"]
