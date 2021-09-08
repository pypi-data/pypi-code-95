from Utils.StaticUtils import StaticUtils
class TimeZone(object):
    def __init__(self, input_dict):
        self.CountryCode = input_dict.get("CountryCode")
        self.TimeZoneId = input_dict.get("TimeZoneId")
        self.OlsonName = input_dict.get("OlsonName")
        self.IsEnabled = input_dict.get("IsEnabled")
        self.Name = input_dict.get("Name")

    def DateTimeAsUTC(self, string_date):
        if string_date is None:
            return None
        dt = StaticUtils.ParseDate(string_date)
        dt = StaticUtils.ReplaceTZ(dt, self.OlsonName)
        dt = StaticUtils.DateTimeToUTC(dt)
        return dt
    

if __name__ == "__main__":
    tz = TimeZone({"CountryCode": "DK",
        "TimeZoneId": 338,
        "OlsonName": "Europe/Copenhagen",
        "IsEnabled": True,
        "Name": "(UTC+01: 00) Brussels...rid, Paris"})
    tz.DateTimeAsUTC("2021-09-08T07:18:16Z")
    print("test")
    
