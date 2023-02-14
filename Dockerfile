# syntax=docker/dockerfile:1.4

FROM python:3.9-alpine
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["-u", "rt_data.py"]
EXPOSE 8083