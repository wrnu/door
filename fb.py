from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import initialize_app
from time import sleep

cred = credentials.Certificate("door-firebase.json")
initialize_app(cred)

frontdoor = firestore.client().collection('frontdoor')

def get_status():
    return frontdoor.document('status').get().to_dict()

def set_action(a):
    unlock = False
    if a == 'unlock':
        unlock = True
    frontdoor.document('action').set({'unlock': unlock}) 

