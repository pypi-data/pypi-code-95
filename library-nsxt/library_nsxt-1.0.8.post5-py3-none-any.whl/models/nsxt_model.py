class NSXTModel:
    _TAG_SCOPE_KEY = "scope"
    _TAG_VALUE_KEY = "tag"

    def __init__(self, id, display_name, revision):
        self.id = id
        self.display_name = display_name
        self.revision = revision

    def to_json(self):
        """
        Serializes the model into its JSON representation.

        :return: The json representation of the model.
        :rtype: dict
        """
        raise NotImplementedError("Nsxt model must implement a to_json method.")

    @classmethod
    def from_json(cls, raw_json):
        """
        Deserializes a json into the required model object.

        :param dict raw_json: The raw json dictionary of the model.
        :return: The NSX-T model.
        :rtype: NSXTModel
        """
        raise NotImplementedError("Nsxt model must implement a from_json method.")

    @classmethod
    def _parse_tags(cls, raw_tags):
        """
        Extracts the tags from a tag declaration.

        :param dict raw_tags: The raw tags declaration.
        :return: The parsed tags.
        :rtype: set[(str, str)]
        """
        return {(tag[cls._TAG_SCOPE_KEY], tag[cls._TAG_VALUE_KEY]) for tag in raw_tags}

    @classmethod
    def _build_tags(cls, tags):
        """
        Returns the tags as expected by the NSX-T API.

        :param set[(str, str)] tags: The model tags
        :return: The tags as a ipset tag list.
        :rtype: dict
        """
        return [{
            cls._TAG_SCOPE_KEY: scope,
            cls._TAG_VALUE_KEY: tag
        } for scope, tag in tags]
