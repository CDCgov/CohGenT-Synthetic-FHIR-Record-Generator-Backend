from typing import Any
class FhirResource():

    def __init__(self):
        pass
            
    def __getitem__(self, key: str):
        return self.data[key]