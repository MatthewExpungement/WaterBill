# -*- coding: utf-8 -*-
import scrapy
from WaterBill.items import SessionIDItem

class SessioninfoSpider(scrapy.Spider):
    name = 'sessioninfo'
    start_urls = ['http://cityservices.baltimorecity.gov/water//']
    
    def start_requests(self):
        yield scrapy.Request(url='http://cityservices.baltimorecity.gov/water/')

    def parse(self, response):
        print("getting view state")
        item = SessionIDItem()
        if(response.status != 200):
            #Site might be down. Log error/send email and shut it down.
            print("Non 200 response " + str(response.status))
            sys.exit()
        
        #Need to search through the cookies to find the ASP.NET_SessionId
        cookies = response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(';')
        for cookie in cookies:
            if("Session" in cookie):
                item['sessioncookie'] = cookie.split('=')[1]

        #Grab validation credentials by going to the homepage and grabbing what is generated.
        item['VIEWSTATE'] = response.xpath('//input[@id="__VIEWSTATE"][1]/@value').extract_first()
        item['VIEWSTATEGENERATOR'] = response.xpath('//input[@id="__VIEWSTATEGENERATOR"][1]/@value').extract_first()
        item['EVENTVALIDATION'] = response.xpath('//input[@id="__EVENTVALIDATION"][1]/@value').extract_first()
        

        return item
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