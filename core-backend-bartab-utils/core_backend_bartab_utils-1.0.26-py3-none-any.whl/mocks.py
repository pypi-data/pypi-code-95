def mock_address(
    address_one: str= "250 S Grand Ave",
    address_two: str = None,
    city: str = "Los Angeles",
    state: str = "CA",
    postal_code: str = "90012",
    country: str = 'US',
    lat: float = 34.05328815,
    lng: float = -118.25062277616152
) -> dict:
    address = {
        "address_one": address_one,
        "city": city,
        "state": state,
        "postal_code": postal_code,
        "country": country,
        "geocode": {
            "lat": lat,
            "lng": lng
        }
    }

    if address_two != None and address_two != '':
        address['address_two'] = address_two

    return address
