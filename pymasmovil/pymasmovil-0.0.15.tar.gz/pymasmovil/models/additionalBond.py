class AdditionalBond:
    """
    Class to build OrderItem and Asset additional bonds
    """

    id = ""
    Name = ""
    ExternalIDXenaRC = ""
    AssetId = ""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.__class__, key):
                setattr(self, key, value)
