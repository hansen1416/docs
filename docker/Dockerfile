
FROM ubuntu:18.04

# avoid error "debconf: delaying package configuration, since apt-utils is not installed", not important
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && apt-get update 

# install python3
RUN apt-get -y install jupyter-notebook

RUN mkdir -p /home/docs

WORKDIR /home/docs

COPY entrypoint.sh /

RUN ["chmod", "+x", "/entrypoint.sh"]

EXPOSE 8100/tcp

ENTRYPOINT ["/entrypoint.sh"]
