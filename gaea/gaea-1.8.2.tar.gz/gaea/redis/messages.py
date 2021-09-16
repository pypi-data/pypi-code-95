CHANNEL_PASSWORD_RESET = "PASSWORD_RESET"

CHANNELS = (CHANNEL_PASSWORD_RESET,)


def check_channel(channel):
    return channel in CHANNELS
