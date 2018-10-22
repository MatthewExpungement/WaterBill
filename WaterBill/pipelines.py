import sys
import pymysql.cursors
import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request
import json
import os

class WaterbillPipeline(object):
    def __init__(self):
        try:
            # Connect to the database
            print("----------------------------")
            print(os.environ)
            print(os.environ['sql_server'])
            self.conn = pymysql.connect(host=os.environ['sql_server'],
                                user=os.environ['sql_user'],
                                password=os.environ['sql_password'],
                                db='water',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("SQL Error")
            print(e)
    def process_item(self, item, spider):
        if(spider.name == 'sessioninfo'):
            self.file = open('session_info.json', 'w')
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            self.file.close()
        else:
            try:
                for key,value in item.items():
                    if(item[key] == ''):
                        item[key] = None
                with self.conn.cursor() as cursor:
                    sql = "INSERT INTO water_bills (`Account_Number`, `Service_Address`, `Current_Read_Date`, `Current_Bill_Date`, `Penalty_Date`, `Current_Bill_Amount`, `Previous_Balance`, `Current_Balance`, `Previous_Read_Date`, `Last_Pay_Date`, `Last_Pay_Amount`,`TimeStamp`,`TurnOffDate`,`Searched_Address`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
                    cursor.execute(sql, (item['Account_Number'], item['Service_Address'], item['Current_Read_Date'], item['Current_Bill_Date'], item['Penalty_Date'], item['Current_Bill_Amount'], item['Previous_Balance'], item['Current_Balance'], item['Previous_Read_Date'], item['Last_Pay_Date'], item['Last_Pay_Amount'], item['Timestamp'], item['TurnOffDate'], item['Searched_Address']))
                    self.conn.commit()
            except Exception as e:
                print('Got error {!r}, errno is {}'.format(e, e.args[0]))
                print("----------------------")
                print(cursor._last_executed)

        return item
        

