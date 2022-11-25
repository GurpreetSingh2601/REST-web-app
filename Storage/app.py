import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from receive_orders import ReceivedOrders
from damaged_parts import DamagedParts
import datetime
import time
import yaml
import json
import os
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread 
from sqlalchemy import and_

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

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

create_engine_str = f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}'

logger.info(f"Connecting to database : {hostname}, port : {port}")

DB_ENGINE = create_engine(create_engine_str)
Base.metadata.bind = DB_ENGINE
Base.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def reports_damaged_parts(body):
    pass

    # session = DB_SESSION()

    # dp = DamagedParts(body['damage_cost'],
    #                    body['damage_description'],
    #                    body['damaged_part_qty'],
    #                    body['order_date'],
    #                    body['order_number'],
    #                    body['part_number'],
    #                    body['part_type'],
    #                    body['trace_id'])

    
    # logger.debug(f"Returned event report order details response with ID : {body['trace_id']} with response code 201")
    
    # session.add(dp)

    # session.commit()
    # session.close()

    # return NoContent, 201


def reports_order_details(body):
    pass
    """ Receives a heart rate (pulse) reading """

    # session = DB_SESSION()
    # ro = ReceivedOrders(body['order_date'],
    #                body['order_number'],
    #                body['part_number'],
    #                body['part_price'],
    #                body['part_quantity'],
    #                body['part_type'],
    #                body['trace_id'])

   
    # logger.debug(f"Returned event report order details response with ID : {body['trace_id']} with response code 201")

    # session.add(ro)

    # session.commit()
    # session.close()


    # return NoContent, 201

def get_orders_received_readings(start_timestamp, end_timestamp):
    """ Gets new order received readings after the timestamp """
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%f") #2023-08-29T09:12:33.001
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    readings = session.query(ReceivedOrders).filter(and_(ReceivedOrders.date_created >= start_timestamp_datetime, ReceivedOrders.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for order received readings after %s returns %d results" %(start_timestamp, len(results_list)))
    return results_list, 200

def get_damaged_parts_readings(start_timestamp, end_timestamp):
    """ Gets new damaged parts readings after the timestamp """
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%f") #2023-08-29T09:12:33.001
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    readings = session.query(DamagedParts).filter(and_(DamagedParts.date_created >=start_timestamp_datetime, DamagedParts.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for damaged parts readings after %s returns %d results" %(start_timestamp, len(results_list)))
    return results_list, 200


def process_messages():

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    current_retries = 0
    max_tries = app_config["events"]["max_tries"]
    time_in_seconds = app_config["events"]["seconds"]

    while current_retries < max_tries:
        try:
            logger.info(f"Trying to reconnect to kafka with retry count : {current_retries}")
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except:
            logger.error(f"Connection failed to kafka")
            time.sleep(time_in_seconds)
            current_retries+=1
    
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        print(msg['type'])
        
        if msg["type"] == "OrderedParts": # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            session = DB_SESSION()

            ro = ReceivedOrders(payload['order_date'],
                            payload['order_number'],
                            payload['part_number'],
                            payload['part_price'],
                            payload['part_quantity'],
                            payload['part_type'],
                            payload['trace_id']             
                            
            )

            session.add(ro)

            session.commit()
            session.close()
           

        elif msg["type"] == "DamagedParts": # Change this to your event type
            session = DB_SESSION()
            logger.debug('it gets here')
            dp = DamagedParts(payload['damage_cost'],
                        payload['damage_description'],
                        payload['damaged_part_qty'],
                        payload['order_date'],
                        payload['order_number'],
                        payload['part_number'],
                        payload['part_type'],
                        payload['trace_id']
                        
                        )

            session.add(dp)

            session.commit()
            session.close()
        else:
            logger.debug('Dont know where the message goes')
        # Store the event2 (i.e., the payload) to the DB
        # Commit the new message as being read
        consumer.commit_offsets()
    
def health_check():
    logger.info("Checking for health")
    dictionary = {"message" : "running"}
    return dictionary, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/storage", strict_validation=True, validate_responses=True)



if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
