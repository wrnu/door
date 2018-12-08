from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import initialize_app
from time import sleep

cred = credentials.Certificate("door-firebase.json")
initialize_app(cred)

frontdoor = firestore.client().collection('frontdoor')

def get_locked():
    return frontdoor.document('status').get().to_dict().get('locked')

def set_locked(s):
    frontdoor.document('action').set({'locked': s}) 

def get_unlock(u):
    return frontdoor.document('action').get().to_dict().get('unlock')

def set_unlock(u):
    frontdoor.document('action').set({'unlock': u}) 

