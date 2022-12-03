FROM python:3.10

# Install dependencies

RUN pip install --upgrade pip
RUN pip install pipenv

ENV PROJECT_DIR /home/ncs/zenoh-action/python

WORKDIR ${PROJECT_DIR}

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY . .

CMD ["python", "server.py"]