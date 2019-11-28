#!/usr/bin/env python

import hue
import sys
import signal
import RPi.GPIO as GPIO
import SimpleMFRC522
import logging
import traceback
from time import sleep
from datetime import datetime as dt
from thread import start_new_thread

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

DOOR    = 3
LOCK    = 1
UNLOCK  = 0
HUE_IP  ='192.168.1.103'

fobs = {
#    560550765198:   "Black fob, Warren",
#    584186562352:   "Jeff",
    584208683538:   "Franzi",
#    821866116699:   "Pat",
#    584187199478:   "Takumi",
#    584191065136:   "Jeff's Compass Card",
    822367609801:   "Kevin's Visa",
#    688640897525:   "Will Wristband",
#    622105997585:   "Warren Wristband",
#    484060901810:   "Green Writstband",
    437722577338:   "Jeff's Blue Fob",
#    412213325151:   "Dylan's Debit",
#    549014381766:   "Aaron's Visa",
#    683219655431:   "Joe's ScotiaCard",
    584189237183:   "Jolie's Compass Card",
#    584191278450:   "Georgie's Compass Card",
    584186620377:   "Warren's Compass Card",
#    903303881209:   "Jeff's green fob",
    317517418344:   "Jeff's orange fob",
    354665997279:   "Nida's white fob",
    935462075277:   "Will's Blue fob"
}

reader = SimpleMFRC522.SimpleMFRC522()
hue_bridge  = hue.HouseHue(HUE_IP)

class GracefulKiller:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        cleanup()
        sys.exit(0)

def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.OUT)
    GPIO.output(DOOR, LOCK)

def unlock():
    hue_bridge.connect()
    state = hue_bridge.getFrontDoorState()
    hue_bridge.setFrontDoor(not state.get('on'), state.get('bri'))
    GPIO.output(DOOR, UNLOCK)
    sleep(0.5)
    hue_bridge.setFrontDoor(state.get('on'), state.get('bri'))
    sleep(4.5)
    GPIO.output(DOOR, LOCK)

def cleanup():
    GPIO.cleanup()

def log_status(status, fob_id, fob_desc):
    log.warning("{}: {} - {}".format(status, fob_id, fob_desc))

def rfid():
    try:
        log.info("Starting RFID Process")
        while True:
            fob_id, _ = reader.read()
            if fob_id in fobs.keys():
                log_status('UNLOCK', fob_id, fobs.get(fob_id))
                unlock()
            else:
                log_status('ERROR', fob_id, 'Unkown ID')

            sleep(0.5)
    except Exception as e:
        log.error(str(e))

def main():
    log.info("Starting Main Process")

    while True:
        try:
            rfid()
        except Exception as e:
            log.error(str(e))

if __name__== "__main__":
    killer = GracefulKiller()
    try:
        gpio_init()
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.error(str(e))

    finally:
        cleanup()
        sys.exit(0)

