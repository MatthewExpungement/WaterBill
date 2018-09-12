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
        with open('items.json') as f:
            sessioninfo = json.load(f)
        sessioninfo = sessioninfo[0]

        url = 'http://cityservices.baltimorecity.gov/water/'
        
        #Take the cookies from what was scraped above and add them to the new cookies to be passed.
        cookies = {
            'popup':'seen',
            'ASP.NET_SessionId': sessioninfo['sessioncookie']
        }
        #Same with the different view states.
        post_params = {
            '__VIEWSTATE':  sessioninfo['VIEWSTATE'],
            '__VIEWSTATEGENERATOR': sessioninfo['VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': sessioninfo['EVENTVALIDATION'],
            'ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$btnGetInfoServiceAddress': 'Get Info'
        }

        #Run through all the addresses in our csv to start scraping.
        with open('Addresses.csv', 'r') as csvfile:
            addresses = csv.reader(csvfile)
            for x,row in enumerate(addresses):
                self.log("Row " + str(x))
                address = row[0]
                post_params['ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$ucServiceAddress$txtServiceAddress']= address
                yield scrapy.FormRequest(url=url, callback=self.parseWaterBill, cookies = cookies, method='POST',formdata=post_params, meta={'address':address,'timestamp':datetime.today(),'row_num':str(x)},errback=self.errback_httpbin,dont_filter = True)
    def parseWaterBill(self, response):
        #Check if we found the water bill
        #print("Seconds took to run row " + response.meta['row_num'] + ": " + str(datetime.today() - response.meta['timestamp']) + " seconds.")
        if(len(response.xpath("//span[@id='ctl00_ctl00_rootMasterContent_LocalContentPlaceHolder_lblCurrentBalance']")) == 0):
            print("Couldn't find a water bill for address " + response.meta['address'])
            self.writeFailedCSV(response.meta['address'])
            return None
        wateritem = WaterbillItem()
        table = response.xpath('//table[@class="dataTable"]//tr')
        headers = ['Account Number', 'Service Address', 'Current Read Date', 'Current Bill Date', 'Penalty Date', 'Current Bill Amount', 'Previous Balance', 'Current Balance', 'Previous Read Date', 'Last Pay Date', 'Last Pay Amount','TimeStamp']
        for row in table:
            header = Selector(text=row.extract()).xpath('//th/text()').extract_first()
            value = Selector(text=row.extract()).xpath('//td/descendant::*/text()').extract_first()
            #print(str(header) + " " + str(value))
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
        sys.exit()
    def spider_closed(self, spider):
        self.log("Scraped " + str(spider.stats.get_value('item_scraped_count')) + " in " + str(spider.stats.get_value('finish_time') - spider.stats.get_value('start_time')) + " seconds")
