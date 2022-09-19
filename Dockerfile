FROM python:3.8

RUN mkdir /app

# set GOOGLE_APPLICATION_CREDENTIALS
COPY cloudrobotai-reader-6d85ccb16818.json /app
ENV GOOGLE_APPLICATION_CREDENTIALS /app/cloudrobotai-reader-6d85ccb16818.json

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y git
RUN pip3 install flask 
RUN pip3 install crms
RUN pip3 install dvc[gs]
RUN pip3 install python-dotenv

ADD https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-395.0.0-linux-x86_64.tar.gz .
RUN tar -xf ./google-cloud-cli-395.0.0-linux-x86_64.tar.gz
RUN ./google-cloud-sdk/install.sh

COPY app.py /app/app.py

WORKDIR /app

#CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
#CMD ["crms", "list"]
CMD ["python3", "app.py"]

