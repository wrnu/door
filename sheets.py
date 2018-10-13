import gspread
from oauth2client.service_account import ServiceAccountCredentials

class FOBSheet():
    def __init__(self, name="FOB List"):
        self.gc = None
        self.sheet = None
        self.name = name
        self.authorize()
        
    def authorize(self):
        scope = ['https://spreadsheets.google.com/feeds',
                         'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('/var/secrets/door.json', scope)

        self.gc = gspread.authorize(credentials)

    def getSheet(self):
        return self.gc.open(self.name).sheet1

    def getByID(self, fob_id):
        try:
            self.sheet = self.getSheet()
        except gspread.exceptions.APIError:
            self.authorize()
            self.sheet = self.getSheet()
        finally:    
            values = self.sheet.get_all_values()
            for row in values:
                if fob_id in row:
                    return row
            return []
