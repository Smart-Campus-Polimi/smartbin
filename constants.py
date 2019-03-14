BIN_NAME = "bin0"
#MQTT
HOST = '34.244.160.143'
FILL_LEVEL_FAKE = "smartbin/fill_levels/fake"
FILL_LEVEL_TOPIC = "smartbin/status/"+BIN_NAME

TOPIC_TO_SUBCRIBE_TO = 'response/prediction/trash'
TOPIC_TO_FAKE_TO = 'response/prediction/fake'
#GREENGRASS
HOST = '34.244.160.143'
HOSTV2 = '63.33.41.143'
PORT = '22'
USER = 'ubuntu'
PASS = 'vodafone5G'
KEY = '/home/pi/certs/vf-it-5g.pem'

DESTINATION_FOLDER = '/home/ubuntu/vm1-node-service/raw_field_data'
#DESTINATION_FOLDER2 = '/home/ubuntu/raw_field_data'

ORIGIN_FOLDER = '/home/pi/pictures/'


#MISCELLANEOUS
THRESHOLD_TOF = 240
BIN_HEIGHT = 800.0
TIMER_PHOTO = 5 #seconds
TIMER_DOOR = 10 #seconds

#PATHS
#PICTURE_DIRECTORY = '~/pictures/'


#### GPIO PINS ####
DOOR_SENSOR = 18 #magnetic

#TOF
SENSOR1 = 20 #tof1
SENSOR2 = 16 #tof2
SENSOR_UNSORTED = 21 #tof unsorted
SENSOR_PLASTIC = 26 #tof plastic
