FROM ubuntu:16.04

WORKDIR /home/app/

# install things required for python3.6.9 installation
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y install libssl-dev openssl wget

# download and install python
RUN wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz
RUN tar xzvf Python-3.6.9.tgz
RUN apt-get -y install build-essential liblzma-dev
RUN Python-3.6.9/configure
RUN apt-get -y install zlib1g-dev libbz2-dev
RUN make
RUN make install 
RUN pip3 install --upgrade pip
RUN pip3 install pyqt5

# download and install specdal
RUN git clone https://github.com/EnSpec/SpecDAL.git && pip install SpecDAL/

WORKDIR ../
