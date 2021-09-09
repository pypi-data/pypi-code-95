from cbor2 import dumps, loads


class CBorMessage:

    def as_dict(self) -> dict:
        return {
            k: (
                v.as_dict() if isinstance(v, CBorMessage) else v
            ) for k, v in self.__dict__.items()
        }

    def to_bytes(self) -> bytes:
        return dumps(self.as_dict())

    @classmethod
    def from_bytes(cls, data: bytes) -> 'CBorMessage':
        d = loads(data)
        d.pop("_t", None)
        return cls(**d)
