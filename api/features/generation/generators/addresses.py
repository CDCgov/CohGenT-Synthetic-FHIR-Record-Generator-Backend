from faker import Faker

from api.features.generation.constants import SpecialValues

def generate_address(city: str | None, state: str | None, mask_pii_enabled: bool = False) -> str:
    fake = Faker()

    if mask_pii_enabled:
        line: str = "" # TODO: Swap this to handle $masked once fhir sheets supports primitive masked items.
    else:
        line: str = fake.street_address()

    if not city:
        city = fake.city()
    if not state:
        state = fake.state_abbr()

    county: str = ""
    postalcode: str = ""
    try:
        postalcode: str = fake.zipcode_in_state(state)
    except:
        postalcode: str = fake.zipcode()

    address_string = f"{line}^{city}^{county}^{postalcode}^{state}^US"
    return address_string
