# syntax=docker/dockerfile:1

#FROM tiangolo/uwsgi-nginx:python3.11
FROM python:3.11-slim-buster 

# Install app requirements
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

# Define static files so they can be served direct by nginx without
# being handled by uwsgi
#ENV STATIC_URL /static
#ENV STATIC_PATH /tourtracker_app/static

# Copy app to docker image
COPY . /code
WORKDIR /code

#CMD ["flask --app run run --debug"]
EXPOSE 80
CMD ["flask", " --app run --debug run --no-reload --port 80"]
#CMD ["python",  "run.py"]


#ENV PYTHONPATH=/app


#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh

#RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh

#ENTRYPOINT ["/entrypoint.sh"]

#CMD ["/start.sh"]
