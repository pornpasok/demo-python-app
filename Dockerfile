FROM python:3.7

ENV ELK_ENDPOINT
ENV ISHOP_CONNECTOR
ENV PASSWORD
ENV USERNAME

RUN mkdir /app
WORKDIR /app
ADD ./app/ /app/
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/app/main.py"]