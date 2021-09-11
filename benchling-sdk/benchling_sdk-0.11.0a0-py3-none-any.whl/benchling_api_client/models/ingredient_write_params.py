from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.ingredient_amount import IngredientAmount
from ..models.ingredient_measurement_units import IngredientMeasurementUnits

T = TypeVar("T", bound="IngredientWriteParams")


@attr.s(auto_attribs=True, repr=False)
class IngredientWriteParams:
    """  """

    _amount: IngredientAmount
    _component_entity_id: str
    _units: IngredientMeasurementUnits
    _catalog_identifier: Optional[str]
    _component_lot_container_id: Optional[str]
    _component_lot_entity_id: Optional[str]
    _component_lot_text: Optional[str]
    _notes: Optional[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("amount={}".format(repr(self._amount)))
        fields.append("component_entity_id={}".format(repr(self._component_entity_id)))
        fields.append("units={}".format(repr(self._units)))
        fields.append("catalog_identifier={}".format(repr(self._catalog_identifier)))
        fields.append("component_lot_container_id={}".format(repr(self._component_lot_container_id)))
        fields.append("component_lot_entity_id={}".format(repr(self._component_lot_entity_id)))
        fields.append("component_lot_text={}".format(repr(self._component_lot_text)))
        fields.append("notes={}".format(repr(self._notes)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "IngredientWriteParams({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        amount = self._amount.to_dict()

        component_entity_id = self._component_entity_id
        units = self._units.value

        catalog_identifier = self._catalog_identifier
        component_lot_container_id = self._component_lot_container_id
        component_lot_entity_id = self._component_lot_entity_id
        component_lot_text = self._component_lot_text
        notes = self._notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "componentEntityId": component_entity_id,
                "units": units,
                "catalogIdentifier": catalog_identifier,
                "componentLotContainerId": component_lot_container_id,
                "componentLotEntityId": component_lot_entity_id,
                "componentLotText": component_lot_text,
                "notes": notes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        amount = IngredientAmount.from_dict(d.pop("amount"))

        component_entity_id = d.pop("componentEntityId")

        units = IngredientMeasurementUnits(d.pop("units"))

        catalog_identifier = d.pop("catalogIdentifier")

        component_lot_container_id = d.pop("componentLotContainerId")

        component_lot_entity_id = d.pop("componentLotEntityId")

        component_lot_text = d.pop("componentLotText")

        notes = d.pop("notes")

        ingredient_write_params = cls(
            amount=amount,
            component_entity_id=component_entity_id,
            units=units,
            catalog_identifier=catalog_identifier,
            component_lot_container_id=component_lot_container_id,
            component_lot_entity_id=component_lot_entity_id,
            component_lot_text=component_lot_text,
            notes=notes,
        )

        ingredient_write_params.additional_properties = d
        return ingredient_write_params

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def amount(self) -> IngredientAmount:
        return self._amount

    @amount.setter
    def amount(self, value: IngredientAmount) -> None:
        self._amount = value

    @property
    def component_entity_id(self) -> str:
        return self._component_entity_id

    @component_entity_id.setter
    def component_entity_id(self, value: str) -> None:
        self._component_entity_id = value

    @property
    def units(self) -> IngredientMeasurementUnits:
        return self._units

    @units.setter
    def units(self, value: IngredientMeasurementUnits) -> None:
        self._units = value

    @property
    def catalog_identifier(self) -> Optional[str]:
        return self._catalog_identifier

    @catalog_identifier.setter
    def catalog_identifier(self, value: Optional[str]) -> None:
        self._catalog_identifier = value

    @property
    def component_lot_container_id(self) -> Optional[str]:
        return self._component_lot_container_id

    @component_lot_container_id.setter
    def component_lot_container_id(self, value: Optional[str]) -> None:
        self._component_lot_container_id = value

    @property
    def component_lot_entity_id(self) -> Optional[str]:
        return self._component_lot_entity_id

    @component_lot_entity_id.setter
    def component_lot_entity_id(self, value: Optional[str]) -> None:
        self._component_lot_entity_id = value

    @property
    def component_lot_text(self) -> Optional[str]:
        return self._component_lot_text

    @component_lot_text.setter
    def component_lot_text(self, value: Optional[str]) -> None:
        self._component_lot_text = value

    @property
    def notes(self) -> Optional[str]:
        return self._notes

    @notes.setter
    def notes(self, value: Optional[str]) -> None:
        self._notes = value
