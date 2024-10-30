# Use an official Python runtime as a parent image
FROM python:3.12.6-alpine

RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev libmagic

LABEL maintainer="fachrur.rozi@erasysconsulting.com"

ENV PYTHONUNBUFFERED=1

# Copy the current directory contents into the container at /code/
COPY . /code/
COPY .env.example /code/.env

WORKDIR /code/
# RUN chown -R www-data:www-data /code/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /code/requirements.txt
RUN pip install gunicorn

EXPOSE 8000
# Run start.sh
ENTRYPOINT ["sh", "start.sh"]
