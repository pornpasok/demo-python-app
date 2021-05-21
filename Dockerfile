FROM python:3.7

ARG ELK_ENDPOINT
ARG ISHOP_CONNECTOR
ARG PASSWORD
ARG USERNAME

RUN mkdir /app
WORKDIR /app
ADD ./app/ /app/
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/app/main.py"]