# -*- coding: utf-8 -*-
from scrapy.item import Item,Field
# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class SessionIDItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    #Session Stuff
    sessioncookie = Field()
    VIEWSTATE = Field()
    VIEWSTATEGENERATOR = Field()
    EVENTVALIDATION = Field()
    pass
class WaterbillItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Account_Number=Field()
    Service_Address=Field()
    Current_Read_Date=Field()
    Current_Bill_Date=Field()
    Penalty_Date=Field()
    Current_Bill_Amount=Field()
    Previous_Balance=Field()
    Current_Balance=Field()
    Previous_Read_Date=Field()
    Last_Pay_Date=Field()
    Last_Pay_Amount=Field()
    Timestamp = Field()
    TurnOffDate = Field()
    Searched_Address = Field()
    pass
