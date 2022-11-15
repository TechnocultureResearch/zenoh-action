FROM eclipse/zenoh:latest
FROM python:3.9

COPY . .
#RUN pip install maturin>=0.12.18 

#RUN cargo install --path .


#RUN pip install --upgrade pip && \ 
#    pip install eclipse-zenoh && \
#    export PATH="$HOME/.local/bin:$PATH" && \
#    maturin build --release && \
#    pip install ./target/wheels/

CMD ["python3", "./main.py"]
