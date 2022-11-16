from fileinput import filename
import connexion
import json
import datetime
from connexion import NoContent
import requests
import yaml
import time
import logging
import logging.config
import random
import uuid
import os
from pykafka import KafkaClient

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

def generate_trace_id():
    trace_id = str(random.randint(1,99999999999)) 
    return trace_id

current_retries = 0
max_tries = 20
time_in_seconds = 5
while current_retries < max_tries:
    try:
        host = str(app_config["events"]["hostname"]) +':' +str(app_config["events"]["port"])
        client = KafkaClient(hosts=host)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
        break
    except:
        print("connection refused to kafka client")
        time.sleep(time_in_seconds)
        current_retries+=1

def reports_order_details(body):
    x = generate_trace_id()
    body["trace_id"] = x
    print(x)

    logger.info(f"Received event report order details with a unique id of {x}")

    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config["orders/received"]['url'] ,json=body, headers=headers)
    # logger.info(f"Returned event report order details response with ID : {x} with response code {response.status_code}")
    msg = { "type": "OrderedParts","datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201

def reports_damaged_parts(body):
    x = generate_trace_id()
    body["trace_id"] = x
    print(body['trace_id'])
    
    logger.info(f"Received event report damaged part with a unique id of {x}")

    #headers = {"content-type": "application/json"}
    #response = requests.post(app_config["parts/damaged"]['url'] ,json=body, headers=headers)
    msg = { "type": "DamagedParts","datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Returned event damaged part response with ID : {x} with response code 201")
    return NoContent, 201
    

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)
app.run(port=8080) 