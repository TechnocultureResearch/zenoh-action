FROM eclipse/eclipse/zenoh:latest

ADD ./ /

ARG key="Genotyper/1/DNAsensor/1/start"

ENTRYPOINT [ "python3", './zenoh-action-client.py' ]

