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
    openjdk-8-jre=8u252-b09-1ubuntu1 \
    python3=3.8.2-0ubuntu2 \
    python3-pip=20.0.2-5ubuntu1 \
    r-base=3.6.3-2

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt
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


# Set working directory and start draw
WORKDIR /app/bin
CMD [ "python3" "./gui_app.py" ] 

# Test installations
# WORKDIR /app/tests
# RUN ./test_installations_in_docker.sh
