FROM python:3.7-buster

# RUN pip install jupyter

RUN python -m pip install numpy scipy matplotlib ipython jupyter pandas sympy nose

RUN mkdir -p /home/docs

WORKDIR /home/docs

COPY entrypoint.sh /

RUN ["chmod", "+x", "/entrypoint.sh"]

EXPOSE 8100/tcp

ENTRYPOINT ["/entrypoint.sh"]