
class NSX_Rules:
    def __init__(self, section_name, section_id, rules, revision):
        self.section_name = section_name
        self.section_id = section_id
        self.rules = rules
        self.revision = revision

    def to_json(self):
        json = {
            "resource_type": "FirewallSection",
            "description": "",
            "id": self.section_id,
            "display_name": self.section_name,
            "tags": [],
            "section_type": "LAYER3",
            "is_default": False,
            "stateful": True,
            "rules": self.rules,
            "_revision": self.revision
                }
        return json

class NSX_Sections:
    def __init__(self, section_name):
        self.section_name = section_name

    def to_json(self):
        json = {
                "display_name": self.section_name,
                "section_type": "LAYER3",
                "stateful": True,
                }
        return json