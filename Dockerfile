# setup python version
FROM python:3.6-alpine

MAINTAINER Emmanuel Eleam

# use a working directory
WORKDIR /usr/src/app

# copy my requirements.txt to the current working directory set
COPY requirements.txt .

# run my requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy the entire project
COPY . .

# create a user that will run the application using docker
RUN adduser -D emmanuel
USER emmanuel
