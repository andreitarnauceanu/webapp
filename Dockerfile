FROM centos:latest
MAINTAINER Andrei Tarnauceanu "linuxacademystudent@gmail.com"
RUN yum update -y
RUN yum install git curl -y
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install flask
RUN pip install boto3
RUN pip install Pillow
RUN git clone https://github.com/andreitarnauceanu/utils.git
RUN pip install utils/.
ADD . /app
WORKDIR /app
EXPOSE 80
CMD ["python", "app.py"]
