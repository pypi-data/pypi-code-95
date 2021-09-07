class DisplayHandler():
    def __init__(self):
        self.hours = None
        self.minutes = None
        self.on_property_change = None

    def timedelta_to_display(self, timedelta):
        if timedelta.days < 0:
            timedelta = abs(timedelta)
        hours = timedelta.seconds // 3600
        minutes = (timedelta.seconds // 60) % 60

        isChanged = False
        if (self.hours != hours):
            self.hours = hours
            isChanged = True

        if (self.minutes != minutes):
            self.minutes = minutes
            isChanged = True
        
        if (isChanged and self.on_property_change is not None):
            self.on_property_change(self.hours, self.minutes)

        return [hours, minutes]