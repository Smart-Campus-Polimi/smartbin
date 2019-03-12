
#MQTT
HOST = '34.244.160.143'
FILL_LEVEL_TOPIC = "smartbin/fill_levels"

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

TOPIC_TO_SUBCRIBE_TO = 'response/prediction/trash'


#MISCELLANEOUS
THRESHOLD_TOF = 200
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