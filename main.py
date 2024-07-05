import paho.mqtt.client as paho
import json
import time
import pynmea2
import os
import logging
import threading
from collections import deque 

from   logging.handlers import RotatingFileHandler

# total amount of GPS position we can store when publishing 
# is not possible (ie: because of network outage)
QUEUE_SIZE = 100

'''
    This class is responsible to manage multiple queues.
    Each queue will hold data to be sent by one or multiple consumers.
    Each consumer will consome from its queue.
    Producer will produce in all queues.
    This allows fully asynchronous operation as each consumer will 
    consume and retry at its own rate.
'''
class dequeManager:
    def __init__(self):
        self.deqList = {}
    # returns all elements in all queues 
    def dumpall(self):
        return(self.deqList)
    # create a new q with name qname and max length maxlen
    def create_new_queue(self, qname, maxlen):
        self.deqList[qname] = deque(maxlen = maxlen)
    # add element to the right of all queues
    def add_to_all_q(self, data):
        for q in self.deqList:
            self.deqList[q].appendleft(data)
    # remove element from the left of the queue q
    def pop(self, q):
        if self.len(q) > 0:
            return self.deqList[q].popleft()
        else:
            return None
    # return the number of elements in queue q
    def len(self, q):
        return len(self.deqList[q])
    def maxlen(self, q):
        return self.deqList[q].maxlen()

q = dequeManager()

# x.create_new_queue('mqtt', QUEUE_SIZE)
# x.add_to_all_q('hello')

def on_connect(client, userdata, flags, rc, properties=None):
    if (rc == 0):
        logger.debug('MQTT connected successfully')
    else:
        logger.debug("MQTT did not successfully connect.  Return code=%d", rc)

def on_disconnect(client, userdata, rc):
    logger.debug('MQTT disconnected. Reconnecting...')

def ReqLocation (ser):
    reqTimeout = 3
    tempPayload = {}

    logger.debug('Looking for location information')

    # move pointer to end of file to have fresh data 
    # seek() cannot be used as /dev/ttyNMEA0 will be non-seekable
    # will use read to discard all data and get fresh one
    ser.read()

    startTime = time.time()
    while ((time.time() - startTime) < (reqTimeout)):

        line = ser.readline()

        if line.startswith('$'):
            try:
                msg = pynmea2.parse(line)
                if msg.sentence_type == 'GGA':
                    lat = msg.latitude
                    lon = msg.longitude
                    num_sats = msg.num_sats
                    altitude = msg.altitude
                    altitude_units = msg.altitude_units
                    horizontal_dil = msg.horizontal_dil
                    gps_qual = msg.gps_qual
                    if (gps_qual != 0):
                        tempPayload = {'timestamp' : msg.timestamp.isoformat(), 'lat': lat, 'lon': lon, 'num_sats': num_sats, 'altitude': altitude, 'altitude_units': altitude_units, 'horizontal_dil': horizontal_dil, 'gps_qual': gps_qual}
                    else:
                        tempPayload = {'gps_qual': gps_qual, 'num_sats': num_sats}
                    logger.debug('Received NMEA location data: {}'.format(tempPayload))
                    return tempPayload
            except:
                    logger.debug('NMEA stream parse error')
    logger.debug('Failed to receive location data; giving up')
    return None

'''
  This class will gather the GPS data from the cellular module
  It will use the serial port defined in env variable IR_GPS
  The serial port is treated as a file and already open in __main__ block
  It appends the GPS coords to the left of the deque (double-ended queue)
  Appending items to a deque is a thread-safe operation, no lock needed
'''
class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name

    def run(self):
        while True:
            logger.debug('Starting loop')

            tempPayload = {}

            #Location
            locationData = ReqLocation(gpsser)
            if (ALWAYS_REPORT):
                if (locationData is None):
                    tempPayload['fix_status'] = "no_stream"
                elif (locationData.get('gps_qual', 0) == 0):
                    tempPayload['fix_status'] = "no_fix"
                else:
                    tempPayload['fix_status'] = "success"

            if (locationData is not None):
                if (locationData.get('gps_qual', 0) !=0 or ALWAYS_REPORT):
                    tempPayload['location'] = locationData
                    # enqueue this payload to be sent - if queue is full oldest items is dropped
                    q.add_to_all_q(tempPayload)
        return

'''
  This class will watch the deque (double-ended queue) for new entries
  If found, it takes it from the left on the deque (oldest)
  As a reminder, producer adds new values to the right of the deque
'''
class ConsumerMQTTThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerMQTTThread,self).__init__()
        self.target = target
        self.name = name
        self.qname = 'mqtt'
        q.create_new_queue(self.qname, QUEUE_SIZE)
        return

    def run(self):
        while True:
            if q.len(self.qname) > 0:
                locationData = q.pop(self.qname)
                logger.debug('Consuming {} from queue'.format(str(locationData)))
                timestamp = int(time.time() * 1000)
                tempPayload = {}
                tempPayload['timestamp'] = timestamp
                tempPayload['identifier'] = sn
                if (locationData.get('gps_qual', 0) !=0 or ALWAYS_REPORT):
                    tempPayload['location'] = locationData
                    tempJSON = json.dumps(tempPayload, indent=4)
                    logger.debug('Publishing message from QUEUE -> MQTT')
                    mqttClient.publish(topic,tempJSON,qos=MQTT_QOS)
            time.sleep(1)
        return

if __name__ == '__main__':

    # Get GPS device details from ENV variable
    IR_GPS = os.getenv('IR_GPS')

    MQTT_BROKER = os.getenv('MQTT_BROKER')
    MQTT_PORT = int(os.getenv('MQTT_PORT'))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
    MQTT_USE_TLS = int(os.getenv('MQTT_USE_TLS'))
    MQTT_BASE_TOPIC = os.getenv('MQTT_BASE_TOPIC')
    MQTT_QOS = int(os.getenv('MQTT_QOS'))

    LOOP_INTERVAL = int(os.getenv('LOOP_INTERVAL'))
    DEBUG_VERBOSE = int(os.getenv('DEBUG_VERBOSE'))
    ALWAYS_REPORT = int(os.getenv('ALWAYS_REPORT'))

    CAF_APP_LOG_DIR = os.getenv("CAF_APP_LOG_DIR", "/tmp")

    # We will be using a separate log file to keep the size under control
    log_file_path = os.path.join(CAF_APP_LOG_DIR, "iox-router-loc.log")

    logger = logging.getLogger(__name__)
    if (DEBUG_VERBOSE == 1):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(log_file_path, maxBytes=5000000, backupCount=1)
    log_format = logging.Formatter('[%(asctime)s][%(threadName)s]{%(pathname)s:%(lineno)d}%(levelname)s- %(message)s')
    handler.setFormatter(log_format)
    logger.addHandler(handler)

    sn = os.getenv('CAF_SYSTEM_SERIAL_ID')
    topic = MQTT_BASE_TOPIC + "/" + sn

    logger.info('-------------------------------------------')
    logger.info('CONFIGURATION:')
    logger.info("ROUTER SERIAL NUM: %s", sn)
    logger.info("IR_GPS: %s", IR_GPS)
    logger.info("LOOP_INTERVAL: %d", LOOP_INTERVAL)
    logger.info("MQTT_BROKER: %s", MQTT_BROKER)
    logger.info("MQTT_PORT: %d", MQTT_PORT)
    logger.info("MQTT_USERNAME: %s", MQTT_USERNAME)
    logger.info("MQTT_PASSWORD: %s", MQTT_PASSWORD)
    logger.info("MQTT_USE_TLS: %d", MQTT_USE_TLS)
    logger.info("MQTT_QOS: %d", MQTT_QOS)
    logger.info("MQTT_TOPIC: %s", topic)
    logger.info("DEBUG_VERBOSE: %d", DEBUG_VERBOSE)
    logger.info("ALWAYS_REPORT: %d", ALWAYS_REPORT)

    # mqttClient = paho.Client()
    mqttClient = paho.Client(paho.CallbackAPIVersion.VERSION2)
    mqttClient.reconnect_delay_set(min_delay=5, max_delay=60)
    mqttClient.on_connect = on_connect
    mqttClient.on_disconnect = on_disconnect
    mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    if (MQTT_USE_TLS == 1):
        mqttClient.tls_set()

    mqttSuccess = False
    while (mqttSuccess == False):
        try:
            logger.debug('Attempting to connect to MQTT data broker.')
            mqttClient.connect(MQTT_BROKER, MQTT_PORT)
            mqttSuccess = True
        except:
            logger.debug('Having trouble connecting to MQTT data broker.  Will try again.')
            time.sleep(5)

    mqttClient.loop_start()

    # need to add error handling
    gpsser = open(IR_GPS, "r", encoding='utf-8')

    '''
      The producer will gather GPS data and add them to deque "q"
      The Consumers will watch the queue, and will publish data in the queue
    '''
    p = ProducerThread(name='producer')
    c = ConsumerMQTTThread(name='consumer')

    p.start()
    c.start()

