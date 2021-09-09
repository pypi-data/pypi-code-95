from fhir.resources.claim import Claim
from fhir.resources import backboneelement, domainresource


class ClaimTopicMessage(backboneelement.BackboneElement):
    """ClaimTopicMessage is the result of an insight engine.
    """

    resource_type = "ClaimTopicMessage"

    def __init__(self, jsondict=None, strict=True):
        """ Initialize all valid properties.

        :raises: FHIRValidationError on validation errors, unless strict is False
        :param dict jsondict: A JSON dictionary to use for initialization
        :param bool strict: If True (the default), invalid variables will raise a TypeError
        """

        self.clientId = None

        self.transactionId = None

        self.context = None

        self.claim = None

        self.ttl = None

        super(ClaimTopicMessage, self).__init__(jsondict=jsondict, strict=strict)

    def elementProperties(self):
        js = super(ClaimTopicMessage, self).elementProperties()
        js.extend(
            [
                ("clientId", "clientId", str, "string", False, None, False,),
                ("transactionId", "transactionId", str, "string", False, None, False,),
                ("context", "context", str, "string", False, None, False,),
                ("claim", "claim", Claim, "Claim", False, None, False,),
                ("ttl", "ttl", int, "positiveInt", False, None, False,),
            ]
        )
        return js

    @classmethod
    def dictToObject(cls, dict):
        if dict is None:
            return None
        obj = ClaimTopicMessage()

        obj.clientId = dict.get('clientId', None)

        obj.transactionId = dict.get('transactionId', None)

        obj.context = dict.get('context', None)

        obj.claim = Claim(jsondict=dict.get('claim', None))

        obj.ttl = dict.get('ttl', None)
        return obj
