#Water Bill Scraper

##TLDR
Scrapes about 220,000 water bills from the Baltimore City Water Bill Website

##Description
This was designed to scrape water bills out of the Baltimore City Water Bill website. Make sure you are in compliance with all laws. We disclaim all liability.

This is a dockerized app that uses the python framework scrapy. The resulting information is saved into a mysql table. It was my first time experimenting with scrapy.

##Use
Install docker and docker compose on your server. Locate the Docker folder and in that folder run the command docker-compose up -d. This will launch the app. The app created two docker containers. One is the mysql container and the other is the app container. A shell script in the main folder called ss.sh will run automatically. 

This script runs the first spyder which grabs and saves the session information from the water bill site. The second command runs the second spyder which will run through a csv of account numbers, searching each one, and recording the infromation into the mysql database. 

Included in another csv called Real_Property_Taxes.csv which is from the open baltimore website. You can modify the second spyder slightly to have it run addresses instead of account numbers.