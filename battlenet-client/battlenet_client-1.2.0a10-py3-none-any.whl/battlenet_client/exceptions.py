
class BattleNetError(Exception):
    """Base Exception for the Battlenet API"""
    pass


class InvalidClientError(BattleNetError):
    """Exception for invalid client being using, IE WOW API client used for Overwatch API endpoint"""
    pass
