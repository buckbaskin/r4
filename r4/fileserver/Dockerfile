FROM python:3.5.2
ENV PYTHONUNBUFFERED 1  
RUN mkdir /config
COPY ../../requirements/fileserver/requirements.txt /config/requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r /config/requirements.txt
RUN mkdir /src
RUN echo Done building r4.
WORKDIR /src
