from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.ingredient_amount import IngredientAmount
from ..models.ingredient_component_entity import IngredientComponentEntity
from ..models.ingredient_component_lot_container import IngredientComponentLotContainer
from ..models.ingredient_component_lot_entity import IngredientComponentLotEntity
from ..models.ingredient_measurement_units import IngredientMeasurementUnits

T = TypeVar("T", bound="Ingredient")


@attr.s(auto_attribs=True, repr=False)
class Ingredient:
    """  """

    _amount: IngredientAmount
    _component_entity: IngredientComponentEntity
    _component_lot_container: IngredientComponentLotContainer
    _component_lot_entity: IngredientComponentLotEntity
    _has_parent: bool
    _units: IngredientMeasurementUnits
    _catalog_identifier: Optional[str]
    _component_lot_text: Optional[str]
    _notes: Optional[str]
    _target_amount: Optional[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("amount={}".format(repr(self._amount)))
        fields.append("component_entity={}".format(repr(self._component_entity)))
        fields.append("component_lot_container={}".format(repr(self._component_lot_container)))
        fields.append("component_lot_entity={}".format(repr(self._component_lot_entity)))
        fields.append("has_parent={}".format(repr(self._has_parent)))
        fields.append("units={}".format(repr(self._units)))
        fields.append("catalog_identifier={}".format(repr(self._catalog_identifier)))
        fields.append("component_lot_text={}".format(repr(self._component_lot_text)))
        fields.append("notes={}".format(repr(self._notes)))
        fields.append("target_amount={}".format(repr(self._target_amount)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Ingredient({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        amount = self._amount.to_dict()

        component_entity = self._component_entity.to_dict()

        component_lot_container = self._component_lot_container.to_dict()

        component_lot_entity = self._component_lot_entity.to_dict()

        has_parent = self._has_parent
        units = self._units.value

        catalog_identifier = self._catalog_identifier
        component_lot_text = self._component_lot_text
        notes = self._notes
        target_amount = self._target_amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "componentEntity": component_entity,
                "componentLotContainer": component_lot_container,
                "componentLotEntity": component_lot_entity,
                "hasParent": has_parent,
                "units": units,
                "catalogIdentifier": catalog_identifier,
                "componentLotText": component_lot_text,
                "notes": notes,
                "targetAmount": target_amount,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        amount = IngredientAmount.from_dict(d.pop("amount"))

        component_entity = IngredientComponentEntity.from_dict(d.pop("componentEntity"))

        component_lot_container = IngredientComponentLotContainer.from_dict(d.pop("componentLotContainer"))

        component_lot_entity = IngredientComponentLotEntity.from_dict(d.pop("componentLotEntity"))

        has_parent = d.pop("hasParent")

        units = IngredientMeasurementUnits(d.pop("units"))

        catalog_identifier = d.pop("catalogIdentifier")

        component_lot_text = d.pop("componentLotText")

        notes = d.pop("notes")

        target_amount = d.pop("targetAmount")

        ingredient = cls(
            amount=amount,
            component_entity=component_entity,
            component_lot_container=component_lot_container,
            component_lot_entity=component_lot_entity,
            has_parent=has_parent,
            units=units,
            catalog_identifier=catalog_identifier,
            component_lot_text=component_lot_text,
            notes=notes,
            target_amount=target_amount,
        )

        ingredient.additional_properties = d
        return ingredient

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
    def component_entity(self) -> IngredientComponentEntity:
        return self._component_entity

    @component_entity.setter
    def component_entity(self, value: IngredientComponentEntity) -> None:
        self._component_entity = value

    @property
    def component_lot_container(self) -> IngredientComponentLotContainer:
        return self._component_lot_container

    @component_lot_container.setter
    def component_lot_container(self, value: IngredientComponentLotContainer) -> None:
        self._component_lot_container = value

    @property
    def component_lot_entity(self) -> IngredientComponentLotEntity:
        return self._component_lot_entity

    @component_lot_entity.setter
    def component_lot_entity(self, value: IngredientComponentLotEntity) -> None:
        self._component_lot_entity = value

    @property
    def has_parent(self) -> bool:
        return self._has_parent

    @has_parent.setter
    def has_parent(self, value: bool) -> None:
        self._has_parent = value

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

    @property
    def target_amount(self) -> Optional[str]:
        return self._target_amount

    @target_amount.setter
    def target_amount(self, value: Optional[str]) -> None:
        self._target_amount = value
