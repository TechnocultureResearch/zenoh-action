FROM eclipse/zenoh:latest

ADD ./ /

#--Adding argument for client ----
ARG key="Genotyper/1/DNAsensor/1/start"

#---- Adding entrypoint for client-----
ENTRYPOINT [ "python3", './zenoh-action-client.py' ]
