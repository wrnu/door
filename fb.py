from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import initialize_app

class FirebaseDoor():

    door = None

    def __init__(self, door='frontdoor'):
        self.door = door
        cred = credentials.Certificate("/opt/door/door-firebase.json")
        initialize_app(cred)
        self.door = firestore.client().collection(self.door)

    def get_locked(self):
        return self.door.document('status').get().to_dict().get('locked')

    def set_locked(self, state):
        self.door.document('status').set({'locked': state}) 

    def get_unlock(self):
        return self.door.document('action').get().to_dict().get('unlock')

    def set_unlock(self, state):
        self.door.document('action').set({'unlock': state}) 

