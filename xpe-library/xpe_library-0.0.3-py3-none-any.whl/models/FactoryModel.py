from typing import Optional

from src.models.BaseModel import BaseModel


def factory_model_from_json(model, payload: dict):
    """
    Build a model

    :param model: A reference model class
    :param payload: JSON with the info about the class
    :return: A new instance of the model
    """
    if payload is None:
        return None  # finish execution
    class_model = model()
    # get all object attributes
    for attr in model.__dict__.keys():
        # check if is attribute or method name
        if not attr.startswith("_"):
            attr_full_name = class_model.get_prefix() + attr
            # check if exist attribute on payload
            if payload.get(attr_full_name) is not None:
                # get value
                value: str = payload.get(attr_full_name)
                # set attribute value to object
                class_model[attr] = value
            # check if is a model inside model
            elif isinstance(class_model[attr], BaseModel):
                class_model[attr] = factory_model_from_json(type(class_model[attr]), payload)

    return class_model


def factory_model_to_dict(model) -> Optional[dict]:
    """
    Convert an object to a dictionary

    :param model: The object to build a dictionary
    :return: A new dictionary with all attributes of the model
    """
    if model is None:
        return None

    # Create a empty dictionary
    model_dict: dict = {}
    for attr in model.__dict__.keys():  # get all attributes of the model
        if not attr.startswith("_"):  # Ignore methods
            attr_full_name = model.get_prefix() + attr  # Build the expected name
            if model[attr] is not None:  # if exist a value
                if isinstance(model[attr], BaseModel):  # is a class model ?
                    sub_dict: dict = factory_model_to_dict(model[attr])  # build the dictionary
                    for key in sub_dict.keys():  # get all keys
                        model_dict[key] = sub_dict[key]  # add sub dictionary inside the original dict
                else:
                    model_dict[attr_full_name] = model[attr]

    return model_dict
