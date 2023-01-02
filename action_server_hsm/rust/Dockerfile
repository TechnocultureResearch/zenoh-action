# Package the Action Server into a deployeable Docker Image

# 1. Build the Project
# -
FROM rust:1.65 as builder
WORKDIR /usr/src/zenoh-action
COPY . .
RUN cargo install --path .

# 2. Package the Executable
# -
#FROM debian:buster-slim as runtime
#RUN apt-get update 
## RUN apt-get install -y extra-runtime-dependencies 
## Install any additional runtime dependencies here
FROM rust:1.65 as runtime
#RUN rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/cargo/bin/zenoh-action /usr/local/bin/zenoh-action
CMD ["zenoh-action"]

