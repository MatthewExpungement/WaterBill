import sys
import pymysql.cursors
import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request
import json
import os

class WaterbillPipeline(object):
    def __init__(self):
        # Connect to the database
        self.conn = pymysql.connect(host=os.environ['sql_server'],
                             user=os.environ['sql_user'],
                             password=os.environ['sql_password'],
                             db='water',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()
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
                    cursor.execute(sql, (item['Account_Number'].encode('utf-8'), item['Service_Address'].encode('utf-8'), item['Current_Read_Date'].encode('utf-8'), item['Current_Bill_Date'].encode('utf-8'), item['Penalty_Date'].encode('utf-8'), item['Current_Bill_Amount'].encode('utf-8'), item['Previous_Balance'].encode('utf-8'), item['Current_Balance'].encode('utf-8'), item['Previous_Read_Date'].encode('utf-8'), item['Last_Pay_Date'].encode('utf-8'), item['Last_Pay_Amount'].encode('utf-8'), item['Timestamp'].encode('utf-8'), item['TurnOffDate'].encode('utf-8'), item['Searched_Address'].encode('utf-8')))
                    self.conn.commit()
            except Exception as e:
                print('Got error {!r}, errno is {}'.format(e, e.args[0]))
                print("----------------------")
                print(cursor._last_executed)

        return item
        

