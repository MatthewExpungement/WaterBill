#This is for a scrapy docker
FROM python:3.6

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#Python
RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN pip3 install requests lxml
#RUN pip3 install pymysql

#Nano
RUN apt-get install nano -y

#GIT
RUN apt-get install git -y

#Make FTP Folder
WORKDIR "/"
RUN mkdir ftpdocs

WORKDIR "/"

EXPOSE 80
EXPOSE 3306
EXPOSE 443

#docker run -t -d -v c:\Dropbox\Projects\WaterBill:/app --name scraper scrapy_server
#docker exec -it scrapy_server /bin/bash
