
def generate_email(name: str | None = None) -> str:
    if name is None:
        return "random@example.com"
    else:
        return f"{name.lower().replace(" ", ".")}@example.com"