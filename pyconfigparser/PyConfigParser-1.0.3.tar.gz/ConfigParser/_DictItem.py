class DictItem:
    def __init__(self, d: dict):
        for k, v in d.items():
            if isinstance(v, dict):
                self.__dict__[k] = DictItem(v)

            else:
                self.__dict__[k] = v

    def to_text(self, indent_level: int) -> str:
        text = "DictItem:\n"
        for k, v in self.__dict__.items():
            if isinstance(v, DictItem):
                text += " "*4*indent_level + f"{k} : {v.to_text(indent_level+1)}\n"
            else:
                text += " "*4*indent_level + f"{k} : {v}\n"
        
        return text.strip()

    def as_dict(self) -> dict:
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, DictItem):
                result[k] = v.as_dict()
            else:
                result[k] = v

        return result
 
