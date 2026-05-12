from faker import Faker

def generate_address(city: str | None, state: str | None) -> str:
    fake = Faker()

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
