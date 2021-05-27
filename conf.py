import datetime
import os

from dotenv import load_dotenv

try:
    load = 1
    token = os.environ['TOKEN']
    print("time is ", datetime.datetime.now())
    print('loaded heroku env variables')
except KeyError:
    load_dotenv()
    load = 0
    print('loaded local dotenv file')
    token = os.environ['token']