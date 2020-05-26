############################################################
# Dockerfile to build DRAW 
############################################################

# Set the base image to ubuntu
FROM ubuntu:20.04

# File Author / Maintainer
MAINTAINER Iwona Gozdziewska

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install platforms
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-8-jre \
    python3 \
    python3-virtualenv \
    r-base=3.6.3-2

# Install packages
RUN python3 -m virtualenv --python=/usr/bin/python3 /opt/venv
COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip install -r requirements.txt
COPY install_packages.R .
RUN Rscript install_packages.R

# Install tools
RUN apt-get update && apt-get install -y \
    bowtie2=2.3.5.1-6build1 \
    fastqc=0.11.9+dfsg-2 \ 
    hisat2=2.1.0-4 \    
    igv=2.4.17+dfsg-1 \
    samtools=1.10-3 \    
    stringtie=2.1.1+ds-2 \
    wget=1.20.3-1ubuntu1

COPY . /app
RUN cd app/tools/ && wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.39.zip && \
    unzip Trimmomatic-0.39.zip && rm Trimmomatic-0.39.zip

WORKDIR /app/bin
CMD . /opt/venv/bin/activate && exec python ./DRAW.py 

# EXPOSE 2000 5000

# CMD ["/bin/bash", "start.sh"]

# CMD . /opt/venv/bin/activate && exec python ./DRAW.py 
# CMD . /opt/venv/bin/activate && exec python ./gui_app.py 
# CMD . /opt/venv/bin/activate && exec python ./master.py 
