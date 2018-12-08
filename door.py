#!/usr/bin/env python

import fb
import hue
import sys
import sheets
import signal
import RPi.GPIO as GPIO
import SimpleMFRC522
from time import sleep
from datetime import datetime as dt
from thread import start_new_thread

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

def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.OUT)
    GPIO.output(DOOR, LOCK)

    fs = sheets.FOBSheet()
    return fs

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

def print_status(status, fob_id, fob_desc):
    print("{}: {} {} - {}".format(dt.now().isoformat(), status, fob_id, fob_desc))
    sys.stdout.flush()

def firebase():
    while True:
        if fb.get_unlock():
            fb.set_locked(False)
            unlock()
            fb.set_locked(True)
        sleep(5)

def rfid():
    fs = init()
    while True:
        fob_id, _ = reader.read()
        if fob_id in fobs.keys():
            print_status('SUCCESS', fob_id, fobs.get(fob_id))
            fb.set_locked(False)
            unlock()
            fb.set_locked(True)
        else:
            row = fs.getByID(str(fob_id))
            if row:
                print_status('SUCCESS', row[0], row[1])
                fb.set_locked(False)
                unlock()
                fb.set_locked(True)
            else:
                print_status('ERROR', fob_id, 'Unkown ID')
                sys.stdout.flush()

def main():
    start_new_thread(firebase, ())
    start_new_thread(rfid, ())
    while True
        sleep(10)

if __name__== "__main__":
    killer = GracefulKiller()
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        sys.exit(0)

