FROM python:3.7-buster

RUN python -m pip install numpy scipy matplotlib ipython jupyter pandas \
sympy nose tabula-py PyMuPDF requests xlrd networkx wordcloud

RUN mkdir -p /home/docs

WORKDIR /home/docs

COPY entrypoint.sh /

RUN ["chmod", "+x", "/entrypoint.sh"]

EXPOSE 8100/tcp

ENTRYPOINT ["/entrypoint.sh"]