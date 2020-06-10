############################################################
# Dockerfile to build DRAW 
############################################################

# Set the base image to ubuntu
FROM ubuntu:20.04

# File Author / Maintainer
MAINTAINER Iwona Gozdziewska

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install OpenJDK and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-8-jre=8u252-b09-1ubuntu1 \
    python3=3.8.2-0ubuntu2 \
    python3-pip=20.0.2-5ubuntu1

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install R
ENV R_VERSION 3.6.1
RUN apt-get install -y curl && curl -O https://cdn.rstudio.com/r/ubuntu-2004/pkgs/r-${R_VERSION}_1_amd64.deb
RUN apt-get install -y ./r-${R_VERSION}_1_amd64.deb
RUN ln -s /opt/R/${R_VERSION}/bin/R /usr/bin/R && ln -s /opt/R/${R_VERSION}/bin/Rscript /usr/bin/Rscript

# Install R dependencies
RUN apt-get install -y libcurl4-openssl-dev libxml2-dev libpng-dev libjpeg-dev
COPY install_packages.R .
RUN Rscript install_packages.R

# Install tools
RUN apt-get update && apt-get install -y \
    bowtie2=2.3.5.1-6build1 \
    fastqc=0.11.9+dfsg-2 \ 
    hisat2=2.1.0-4 \    
    samtools=1.10-3 \    
    stringtie=2.1.1+ds-2 \
    wget=1.20.3-1ubuntu1

COPY . /app
RUN cd app/tools/ && wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.39.zip && \
    unzip Trimmomatic-0.39.zip && rm Trimmomatic-0.39.zip


# Set working directory and start draw
WORKDIR /app/bin
CMD [ "python3", "./gui_app.py" ] 

# Test installations
# WORKDIR /app/tests
# RUN ./test_installations_in_docker.sh