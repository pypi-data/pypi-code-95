from library_nsxt.models import NSXTModel


class NSXTSecurityModel(NSXTModel):
    def __init__(self, id, display_name, parent_path, revision):
        NSXTModel.__init__(self, id, display_name, revision)
        self.parent_path = parent_path

    def get_parent_path(self):
        """
        Retrieves the parent path for the model.

        :return: The parent path.
        :rtype: str
        """
        return self.parent_path

    def get_original_path(self):
        """
        Retrieves the model's path at the time of loading or creation.

        :return: It's own path.
        :rtype: str
        """
        raise NotImplementedError("Nsxt Security model must implement a get_original_path method.")

    def get_path(self):
        """
        Retrieves the model's path.

        :return: It's own path.
        :rtype: str
        """
        raise NotImplementedError("Nsxt model must implement a get_path method.")

    def to_json(self):
        NSXTModel.to_json(self)

    @classmethod
    def from_json(cls, raw_json):
        NSXTModel.from_json(raw_json)
