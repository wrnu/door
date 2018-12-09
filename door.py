#!/usr/bin/env python

import hue
import sys
import sheets
import signal
import RPi.GPIO as GPIO
import SimpleMFRC522
import logging
import traceback
from time import sleep
from datetime import datetime as dt
from thread import start_new_thread
from fb import FirebaseDoor

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
    437722577338:   "Blue Fob",
    584188564421:   "Kevin's Visa",
    412213325151:   "Dylan's Debit",
    549014381766:   "Aaron's Visa",
    683219655431:   "Joe's ScotiaCard",
    584189237183:   "Jolie's Compass Card",
    584191278450:   "Georgie's Compass Card",
    584191717940:   "Will's Compass Card",
    584186620377:   "Warren's Compass Card"
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

def firebase(fb):
    try:
        log.info("Starting Firebase Process")
        while True:
            if fb.get_unlock():
                log_status("UNLOCK", "Firebase action", "USER_ID")
                fb.set_unlock(False)
                fb.set_locked(False)
                unlock()
                fb.set_locked(True)
            sleep(5)
    except Exception as e:
        log.error(str(e), exec_info=True)

def rfid(fb, fs):
    try:
        log.info("Starting RFID Process")
        while True:
            fob_id, _ = reader.read()
            if fob_id in fobs.keys():
                log_status('UNLOCK', fob_id, fobs.get(fob_id))
                fb.set_locked(False)
                unlock()
                fb.set_locked(True)
            else:
                row = fs.getByID(str(fob_id))
                if row:
                    log_status('UNLOCK', row[0], row[1])
                    fb.set_locked(False)
                    unlock()
                    fb.set_locked(True)
                else:
                    log_status('ERROR', fob_id, 'Unkown ID')
    except Exception as e:
        log.error(str(e), exec_info=True)

def main():
    log.info("Starting Main Process")
    fb = FirebaseDoor()
    fs = sheets.FOBSheet()
    start_new_thread(firebase, (fb,))
    start_new_thread(rfid, (fb, fs,))

    while True:
        try:
            sleep(10)
        except Exception as e:
            log.error(e)

if __name__== "__main__":
    killer = GracefulKiller()
    try:
        gpio_init()
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.error(str(e), exec_info=True)

    finally:
        cleanup()
        sys.exit(0)

