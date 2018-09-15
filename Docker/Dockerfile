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



WORKDIR "/"

EXPOSE 3306

#docker run -t -d -v c:\Dropbox\Projects\WaterBill:/app --name scraper -e sql_server='172.17.0.2' -e sql_user='root' -e sql_password='password' -e address_list='Addresses_Sample.csv' scrapy_server
#docker run -t -d -v /home/ubuntu/WaterBill:/app --name scraper -e sql_server='172.17.0.3' scrapy_server
#-e sql_server = '172.17.0.2'
#-e sql_user = 'root'
#-e sql_password = 'password'
#-e address_list = 'Addresses_Sample'

#docker exec -it scraper /bin/bash
#scrapy crawl sessioninfo
#scrapy crawl water