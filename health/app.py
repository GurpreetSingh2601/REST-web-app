import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS, cross_origin
import datetime
from base import Base
import requests
from health import Health
import yaml
import json
import os
import sqlite3
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler

def create_database(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE health
        (id INTEGER PRIMARY KEY ASC,
        receiver VARCHAR NOT NULL,
        storage VARCHAR NOT NULL,
        processing VARCHAR NOT NULL,
        audit VARCHAR NOT NULL,
        last_updated STRING(100) NOT NULL)
    ''')
    conn.commit()
    conn.close()

path = 'health.sqlite'
isExist = os.path.exists(path)
if isExist == True:
    print("Exists")
else:
    create_database(path)

with open("app_conf.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"sqlite:///{path}")
#DB_ENGINE = create_engine("sqlite:///%s" %app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    logger.info('Request has been started')
    session = DB_SESSION()
    results = session.query(Health).order_by(Health.last_updated.desc())
    if not results:
        logger.error("Statistics does not exist")
        return 404
    
    #logger.debug(f"contents of python dictionary {results[-1].to_dict()}")
    logger.info("The request has been completed")
    session.close()
    return results[0].to_dict(), 200

def populate_health():
    """ Periodically update health stats """
    logger.info('Period processing has been started')
    session = DB_SESSION()
    #current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    url_receiver = "http://lab6a.eastus2.cloudapp.azure.com/receiver/health"
    url_storage = "http://lab6a.eastus2.cloudapp.azure.com/storage/health"
    url_processing = "http://lab6a.eastus2.cloudapp.azure.com/processing/health"
    url_audit = "http://lab6a.eastus2.cloudapp.azure.com:8110/audit_log/health"

    headers = {"content-type": "application/json"}
    
    try:
        response_receiver = requests.get(url_receiver, headers=headers)
        if response_receiver.status_code == 200:
            receiver = "running" 
            logger.info(f"Status code received {response_receiver.status_code}")
        else:
            receiver = "Down"
    except:
        receiver = "Down"

    try:
        response_storage = requests.get(url_storage, headers=headers)
        if response_storage.status_code == 200:
            storage = "running" 
            logger.info(f"Status code received {response_storage.status_code}")
        else:
            storage = "Down"
    except:
        storage = "Down"
    
    try:
        response_processing = requests.get(url_processing, headers=headers)
        if response_processing.status_code == 200:
            processing = "running" 
            logger.info(f"Status code received {response_processing.status_code}")
        else:
            processing = "Down"
    except:
        processing = "Down"
    
    try:
        response_audit = requests.get(url_audit, headers=headers)
        if response_audit.status_code == 200:
            audit = "running" 
            logger.info(f"Status code received {response_audit.status_code}")
        else:
            audit = "Down"
    except:
        audit = "Down"
    
    last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    session = DB_SESSION()
    stats = Health(receiver,
        storage,
        processing,
        audit,
        datetime.datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%f"))

    session.add(stats)

    session.commit()
    session.close()

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/health", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)

