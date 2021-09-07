class DisplayHandler():
    def timedelta_to_display(self, timedelta):
        if timedelta.days < 0:
            timedelta = abs(timedelta)
        hours = timedelta.seconds // 3600
        minutes = (timedelta.seconds // 60) % 60

        return [hours, minutes]