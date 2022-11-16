import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS, cross_origin
import datetime
from base import Base
import requests
from stats import Stats
import yaml
import json
import os
import sqlite3
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler

conn = sqlite3.connect('data.sqlite')
c = conn.cursor()
def create_database():

    c = conn.cursor()
    c.execute('''
        CREATE TABLE stats
        (id INTEGER PRIMARY KEY ASC,
        num_orders INTEGER NOT NULL,
        max_part_number INTEGER NOT NULL,
        max_part_price INTEGER,
        num_damaged_part INTEGER,
        last_updated STRING(100) NOT NULL)
    ''')
    conn.commit()
    conn.close()

print('Check if STUDENT table exists in the database:')
listOfTables = c.execute(
  """SELECT name FROM sqlite_master WHERE type='table'
  AND name='stats'; """).fetchall()
 
if listOfTables == []:
    create_database()
    print("Table was not found")
    print("table created")
else:
    print('Table found!')

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine("sqlite:///data.sqlite")
#DB_ENGINE = create_engine("sqlite:///%s" %app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    logger.info('Request has been started')
    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    if not results:
        logger.error("Statistics does not exist")
        return 404
    
    #logger.debug(f"contents of python dictionary {results[-1].to_dict()}")
    logger.info("The request has been completed")
    session.close()
    return results[0].to_dict(), 200

def populate_stats():
    """ Periodically update stats """
    logger.info('Period processing has been started')
    session = DB_SESSION()
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    try:
        last_updated = str(results[0].last_updated)
        a,b = last_updated.split(" ")
        url1 = app_config["orders/received"]["url"]+a+'T'+b+"&end_timestamp="+current_timestamp
        url2 = app_config["parts/damaged"]["url"]+a+'T'+b+"&end_timestamp="+current_timestamp
    
    except IndexError:
        last_updated = '2016-08-29T09:12:33.001000'
        url1 = app_config["orders/received"]["url"]+last_updated+"&end_timestamp="+current_timestamp
        url2 = app_config["parts/damaged"]["url"]+last_updated+"&end_timestamp="+current_timestamp

    headers = {"content-type": "application/json"}

    response_orders_received = requests.get(url1, headers=headers)
    response_damaged_parts = requests.get(url2, headers=headers)
    
    list_orders_received = response_orders_received.json() 
    list_damaged_parts = response_damaged_parts.json()
    logger.info(f"List of damaged parts - {list_damaged_parts}")
    logger.info(f" Length = {len(list_damaged_parts)}")
    # logger.info(f"Number of damage part events received {results[0].num_damagaahed_part} ")
    # logger.info(f"Number of order recieved events received {results[0].num_orders}")

    if response_orders_received.status_code != 200: 
        logger.error(f"Status code received {response_orders_received.status_code}")

    try:
        num_orders = results[0].num_orders + len(list_orders_received)
        max_part_number = results[0].max_part_number
        max_part_price = results[0].max_part_price
        num_damaged_part = results[0].num_damaged_part + len(list_damaged_parts)
    
    except IndexError:
        num_orders = len(list_orders_received)
        max_part_number = 0
        max_part_price = 0
        num_damaged_part = len(list_damaged_parts)

    last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    session = DB_SESSION()
    for i in list_orders_received:
        logger.debug(f"new event with a trace id of {i['trace_id']}")
        if i["part_price"] > max_part_price:
            max_part_price = i["part_price"]
        
    for i in list_orders_received:
        if i["part_number"] > max_part_number:
            max_part_number = i["part_number"]

    session = DB_SESSION()
    stats = Stats(num_orders,
        max_part_number,
        max_part_price,
        num_damaged_part,
        datetime.datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%f"))

    logger.debug(f"Updated statistics values : max_part_number = {max_part_number}, max_part_price = {max_part_price}, num_damaged_parts = {num_damaged_part}")
    logger.info("Period processing has ended.")

    session.add(stats)

    session.commit()
    session.close()

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
