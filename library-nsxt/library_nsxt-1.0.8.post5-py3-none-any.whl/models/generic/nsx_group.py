
class NSX_Group:
    def __init__(self, group_name):
        self.group_name = group_name

    def to_json(self):
        json = {
                "display_name": self.group_name,
                "members": [],
                "membership_criteria": []
                }
        return json

class NSX_Policy_Group:
    def __init__(self, group_name):
        self.group_name = group_name

    def to_json(self):
        json = {
                "display_name": self.group_name
        }
        return json

class NSX_Member_Group:
    def __init__(self, group_id):
        self.group_id = group_id

    def to_json(self):
        json = {
                "target_type": "NSGroup",
                "target_property": "id",
                "op": "EQUALS",
                "value": self.group_id,
                "target_resource": {
                    "is_valid": True
                },
                "resource_type": "NSGroupSimpleExpression"
        }
        return json

class NSX_Policy_Member_Group:
    def __init__(self, group_id):
        self.group_id = group_id

    def to_json(self):
        json = {
                "members": [
                            "/infra/domains/default/groups/" + self.group_id
                ]
        }

        return json

class NSX_Policy_Path_Expression:
    def __init__(self, member_group_id, path_exp_id):
        self.path_exp_id = path_exp_id
        self.member_group_id = member_group_id

    def to_json(self):
        json = {
                "paths": [
                    "/infra/domains/default/groups/" + self.member_group_id
                ],
                "resource_type": "PathExpression",
                "id": self.path_exp_id
        }

        return json