FROM eclipse/zenoh:latest
FROM python:3.9

COPY . .

RUN pip install eclipse-zenoh pydantic pyyaml transitions

CMD ["python3", "./main.py", "-e", "tcp/localhost:7447"]
