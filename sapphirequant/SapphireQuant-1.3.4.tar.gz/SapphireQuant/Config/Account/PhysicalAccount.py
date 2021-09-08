
class PhysicalAccount:
    """
    物理账号
    """
    def __init__(self, user_id, password, broker_id, auth_code, channel_id='CTP'):
        self.user_id = user_id
        self.password = password
        self.encryption_password = ''
        self.channel_id = channel_id
        self.broker_id = broker_id
        self.auth_code = auth_code
        self.fund_unit = '{0}@{1}'.format(self.user_id, self.broker_id)

