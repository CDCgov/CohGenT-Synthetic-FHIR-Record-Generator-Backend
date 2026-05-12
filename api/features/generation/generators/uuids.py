import random
from uuid import UUID

def generate_uuid_identifier() -> str:
    uuid = UUID(int=random.getrandbits(128))
    return str(uuid)
