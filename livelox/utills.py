

def print_green(*args):
    text = " ".join(str(arg) for arg in args)
    print(f"\033[92m{text}\033[0m")


def print_red(*args):
    text = " ".join(str(arg) for arg in args)
    print(f"\033[91m{text}\033[0m")
    

def country_code(country: str | None) -> int | None:
    if not country:
        return None

    return {
        "czechia": 57,
        "denmark": 59,
        "finland": 71,
        "france": 72,
        "germany": 80,
        "israel": 104,
        "japan": 108,
        "italy": 130,
        "norway": 158,
        "sweden": 207,
    }[country.lower()]
