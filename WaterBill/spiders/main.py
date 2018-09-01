import scrapy
import re
import json
from scrapy.http import FormRequest
from scrapy.selector import Selector
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import csv
from datetime import datetime

class QuotesSpider(scrapy.Spider):
    name = "water"

    def start_requests(self):
        self.startCSV()
        yield scrapy.Request(url='http://cityservices.baltimorecity.gov/water/', callback=self.getViewState, errback=self.errback_httpbin)


    def getViewState(self,response):
        #Start by grabbing validation credentials by going to the homepage and grabbing what is generated.
        validation_array = {}
        validation_array['__VIEWSTATE'] = response.xpath('//input[@id="__VIEWSTATE"][1]/@value').extract_first()
        validation_array['__VIEWSTATEGENERATOR'] = response.xpath('//input[@id="__VIEWSTATEGENERATOR"][1]/@value').extract_first()
        validation_array['__EVENTVALIDATION'] = response.xpath('//input[@id="__EVENTVALIDATION"][1]/@value').extract_first()
        
        #Need to search through the cookies to find the ASP.NET_SessionId
        cookies = response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(';')
        for cookie in cookies:
            if("Session" in cookie):
                validation_array['SessionID'] = cookie.split('=')[1]

        #Now we can start running the water bills        
        url = 'http://cityservices.baltimorecity.gov/water/'
        
        cookies = {
            'popup':'seen',
            'ASP.NET_SessionId':validation_array['SessionID']
        }
        post_params = {
            '__VIEWSTATE': validation_array['__VIEWSTATE'],
            '__VIEWSTATEGENERATOR': validation_array['__VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': validation_array['__EVENTVALIDATION'],
            
            'ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$btnGetInfoServiceAddress': 'Get Info'
        }
        with open('Addresses.csv', 'r') as csvfile:
            addresses = csv.reader(csvfile)
            for x,row in enumerate(addresses):
                print("Row " + str(x))
                #address = row[5]
                address = row[0]
                post_params['ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$ucServiceAddress$txtServiceAddress']= address
                yield scrapy.FormRequest(url=url, callback=self.parseWaterBill, cookies = cookies, method='POST',formdata=post_params, meta={'address':address})

    def parseWaterBill(self, response):
        #Check if we found the water bill
        if(len(response.xpath("//span[@id='ctl00_ctl00_rootMasterContent_LocalContentPlaceHolder_lblCurrentBalance']")) == 0):
            print("Couldn't find a water bill for address " + response.meta['address'])
            return None
        water_array = {}
        table = response.xpath('//table[@class="dataTable"]//tr')
        headers = ['Account Number', 'Service Address', 'Current Read Date', 'Current Bill Date', 'Penalty Date', 'Current Bill Amount', 'Previous Balance', 'Current Balance', 'Previous Read Date', 'Last Pay Date', 'Last Pay Amount','TimeStamp']
        for row in table:
            header = Selector(text=row.extract()).xpath('//th/text()').extract_first()
            value = Selector(text=row.extract()).xpath('//td/descendant::*/text()').extract_first()
            print(str(header) + " " + str(value))
            if value == None:
                value = '' #So it populates the excel sheet with a blank spot.s
            #    value = Selector(text=row.extract()).xpath('//td/span/b/text()').extract_first()
            if(header != None and header.strip().replace(':',"") in headers):
                value = value.replace('$','').replace(",",'')
                if("Date" in header and value != ''):
                    #Convert to SQL Datetime Format
                    value = datetime.strptime(value.strip(), '%m/%d/%Y').strftime('%Y-%m-%d')
                water_array[header.strip().replace(':',"")] = value.strip()
        
        print(water_array)
        self.writeDataToCSV(water_array)

    def writeDataToCSV(self,data):
        data['TimeStamp'] = datetime.today().strftime('%Y-%m-%d')
        with open('waterbill.csv', "a",newline='') as csv_file:
            print(data.keys())
            writer = csv.DictWriter(csv_file, fieldnames=data.keys())
            writer.writerow(data)
    def startCSV(self):
        #This is just to put the headers in a new csv
        headers = ['Account Number', 'Service Address', 'Current Read Date', 'Current Bill Date', 'Penalty Date', 'Current Bill Amount', 'Previous Balance', 'Current Balance', 'Previous Read Date', 'Last Pay Date', 'Last Pay Amount','TimeStamp']
        with open('waterbill.csv', "w",newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

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