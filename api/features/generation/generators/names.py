from faker import Faker

def generate_name(masked: bool, gender: str | None = None) -> str:
    fake = Faker()
    if masked:
        return "$masked"
    else:
        # generate a name
        if gender == None:
            return f"{fake.first_name()} {fake.last_name()}"
        elif gender.lower() == "male":
            return f"{fake.first_name_male()} {fake.last_name()}"
        elif gender.lower() == "female":
            return f"{fake.first_name_female()} {fake.last_name()}"
        else:
            return  f"{fake.first_name()} {fake.last_name()}"