import scrapy
import re
import json
from scrapy.http import FormRequest
from scrapy.selector import Selector
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import csv
import sys
from datetime import datetime
import time
import pprint
import json
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from WaterBill.items import WaterbillItem
from WaterBill.items import SessionIDItem
import os
from scrapy.crawler import CrawlerProcess

class WaterSpider(scrapy.Spider):
    name = "water"
    def __init__(self,stats):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.stats = stats 
    @classmethod 
    def from_crawler(cls, crawler): 
      return cls(crawler.stats)
    def start_requests(self):
        #Pull saved session ID Info
        with open('session_info.json') as f:
            #A shell script runs the sessioninfo spyder first which gets and saves the session info in a file that is loaded here.
            sessioninfo = json.load(f)

        url = 'http://cityservices.baltimorecity.gov/water/'
        
        #Take the cookies from what was scraped above and add them to the new cookies to be passed.
        cookies = {
            'popup':'seen',
            'ASP.NET_SessionId': sessioninfo['sessioncookie']
        }
        #Same with the different view states.
        search_type = os.environ['search_type']
        if(os.environ['search_type'] == 'Address'):
            #Address
            param_get_info = 'ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$btnGetInfoServiceAddress'
            param_search_type = 'ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$ucServiceAddress$txtServiceAddress'
        else:
            #Account
            param_get_info = 'ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$btnGetInfoAccount'
            param_search_type = 'ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$txtAccountNumber'

        post_params = {
            '__VIEWSTATE':  sessioninfo['VIEWSTATE'],
            '__VIEWSTATEGENERATOR': sessioninfo['VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': sessioninfo['EVENTVALIDATION'],
            param_get_info: 'Get Info' #Clicks the right button
        }

        #Run through all the account numbers in our csv to start scraping.
        with open('/app/SourceCSVs/' + os.environ['county'] + os.environ['search_type'] + ".csv", 'r') as csvfile:
            accounts = csv.reader(csvfile)
            for x,row in enumerate(accounts):
                self.logger.info("Row " + str(x))
                if(len(row) == 0):
                    self.logger.info("Blank so we're skipping")
                    #This means  one of the rows was blank.
                    continue
                account_or_address = row[0] #The address or account number
                post_params[param_search_type]= account_or_address #This sets the right post key with the address
                yield scrapy.FormRequest(url=url, callback=self.parseWaterBill, cookies = cookies, method='POST',formdata=post_params, meta={'search_type':search_type,'account_or_address':account_or_address,'timestamp':datetime.today(),'row_num':str(x)},errback=self.errback_httpbin,dont_filter = True)
    def parseWaterBill(self, response):
        #Check if we found the water bill if not then write to the failed CSV and return.
        if(len(response.xpath("//span[@id='ctl00_ctl00_rootMasterContent_LocalContentPlaceHolder_lblCurrentBalance']")) == 0):
            print("Couldn't find a water bill for account " + response.meta['account_or_address'])
            self.writeFailedCSV(response.meta['account_or_address'])
            return None
        #I use the item feature in scrapy to store the items.
        wateritem = WaterbillItem()
        wateritem['Searched_Address'] = response.meta['search_type'] #This is a relic of when I searched by addresses.
        table = response.xpath('//table[@class="dataTable"]//tr')
        headers = ['Account Number', 'Service Address', 'Current Read Date', 'Current Bill Date', 'Penalty Date', 'Current Bill Amount', 'Previous Balance', 'Current Balance', 'Previous Read Date', 'Last Pay Date', 'Last Pay Amount','TimeStamp']
        #I can't determine if this actually works because I can't find an address with a shut off notice.
        if(len(response.xpath("//span[@id='ctl00_ctl00_rootMasterContent_LocalContentPlaceHolder_lblTurnOffDate']"))!=0):
            wateritem['TurnOffDate'] = "Yes"
            #wateritem['TurnOffDate'] = Selector(text=row.extract()).xpath("//span[@id='ctl00_ctl00_rootMasterContent_LocalContentPlaceHolder_lblTurnOffDate']").extract_first()
        else:
            wateritem['TurnOffDate'] = 'No'
        for row in table:
            header = Selector(text=row.extract()).xpath('//th/text()').extract_first()
            value = Selector(text=row.extract()).xpath('//td/descendant::*/text()').extract_first()
            if value == None:
                value = '' #So it populates the excel sheet with a blank spot
            if(header != None and header.strip().replace(':',"") in headers):
                value = value.replace('$','').replace(",",'')
                if("Date" in header and value != ''):
                    #Convert to SQL Datetime Format
                    value = datetime.strptime(value.strip(), '%m/%d/%Y').strftime('%Y-%m-%d')
                wateritem[header.strip().replace(':',"").replace(' ','_')] = value.strip()
        wateritem['Timestamp'] = datetime.today().strftime('%Y-%m-%d')
        return wateritem

    def writeFailedCSV(self,address):
        #This creates a Fail CSV file so you can investigate as to why it failed. This usually works better with addresses.
        with open('failed.csv',"a",newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([address])
    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        print("Error in HTTP Request!")
        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
    def spider_closed(self, spider):
        self.logger.info("Scraped " + str(spider.stats.get_value('item_scraped_count')) + " in " + str(spider.stats.get_value('finish_time') - spider.stats.get_value('start_time')) + " seconds")
