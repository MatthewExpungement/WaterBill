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

WORKDIR "/app"
#RUN ["chmod", "+x", "start.sh"]
ENTRYPOINT ["./app/start.sh"]