from datetime import date
from uuid import uuid4

class PatientMeta():
    def __init__(self, event_date: date, name: str | None, sex: str | None):
        self.id = str(uuid4())
        self.event_date = event_date
        self.name = name
        self.sex = sex
        self.generate_until_date: date | None = None
    
    def update_name(self, name: str):
        self.name = name
        
    def update_sex(self, sex: str):
        self.sex = sex
    
    def set_until_date(self, until_date: date):
        self.generate_until_date = until_date