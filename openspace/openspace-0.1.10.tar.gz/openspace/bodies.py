class WGS84:
    def __init__(self):
        self.equatorial_radius = 6378137
        self.flattening = 1/298.257223563
        self.angular_rate = 72.92115e-6
        self.mu = 3986004.418e8

class Earth:
    def __init__(self, geodetic_model=WGS84()):
        self.equatorial_radius = geodetic_model.equatorial_radius
        self.flattening = geodetic_model.flattening
        self.angular_rate = geodetic_model.angular_rate
        self.mu = geodetic_model.mu
