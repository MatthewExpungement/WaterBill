# Water Bill Scraper

## TLDR
Scrapes water bills in bulk from the Baltimore City Water Bill Website. This can be for either Baltimore City or Baltimore County. The app can pull based on account number or address and includes a list of a large amount of both for both the city and the county. This is a dockerized app that uses the python framework scrapy. The resulting information is saved into a mysql table.

## Legal
 Make sure you are in compliance with all laws. We disclaim all liability. 

## Use
This runs using docker so make sure it is installed. 

<pre>
cd WaterBill chmod +x start.sh #Otherwise the docker entrypoint runs into permission issues.
docker network create --driver bridge waternet
docker run -p 3306:3306 --name wb_sql -v /path/to/mysql/folder:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=example --network waternet -d mysql:8.0.12 
cd WaterBill/Docker/scraper
docker build -t waterbill_server .
docker inspect -f "{{ .NetworkSettings.Networks.waternet.IPAddress }}" wb_sql
docker run -t -d -v /path/to/WaterBill:/app --name balt_county_accounts -e sql_server='[the ip address output above]' -e sql_user='root' -e sql_password='example' -e county='BaltimoreCounty' -e search_type='Accounts' --network waternet waterbill_server
</pre>

There are several enviornment variables you can change when running the scraper.
<pre>
-e sql_server='172.18.0.2' #This will be different. To get IP of your sql use docker inspect -f "{{ .NetworkSettings.Networks.waternet.IPAddress }}" wb_sql
-e sql_user='root' 
-e sql_password='example'
-e county='BaltimoreCounty' #Either BaltimoreCity or BaltimoreCounty
-e search_type='Accounts' #Either Accounts or Address
</pre>

This script runs the first spyder which grabs and saves the session information from the water bill site. The second command runs the second spyder which will run through a csv of account numbers or addresses, searching each one, and recording the infromation into the mysql database. 

Included in another csv called Real_Property_Taxes.csv which is from the open baltimore website. You can modify the second spyder slightly to have it run addresses instead of account numbers.

Consider using a strong password than example.

If you're interested in collaborating on what to do with this data please let me know!