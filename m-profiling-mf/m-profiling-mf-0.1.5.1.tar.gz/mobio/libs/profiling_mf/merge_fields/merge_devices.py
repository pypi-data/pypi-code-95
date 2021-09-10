from marshmallow import fields, Schema, ValidationError, validate
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import DisplayType
from mobio.libs.profiling_mf.profiling_schema import DeviceSchema


class MergeDevices(BaseMerge):
    def serialize_data(
        self,
        suggest_data,
        profile_data,
        set_suggest_fields,
        set_unique_suggest_values,
        field_key,
        field_property,
        display_type,
        translate_key,
        predict=None,
    ):
        lst_suggest_device = []
        set_device_id = set()
        profile_data = profile_data if profile_data else []
        for device in profile_data:
            if device.get("device_id") not in set_device_id:
                set_device_id.add(device.get("device_id"))
                lst_suggest_device.append(
                    self.__build_value__(value=device, suggest=True)
                )
        suggest_data[field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.OTHER,
            value=lst_suggest_device,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        pass

    def serialize_origin_data(
        self,
        suggest_data,
        origin_data,
        set_suggest_fields,
        set_unique_suggest_values,
        field_key,
        field_property,
        display_type,
        translate_key,
    ):
        lst_suggest_device = []
        if type(origin_data) == list:
            set_device_id = set()
            for device in origin_data:
                if device.get("device_id") not in set_device_id:
                    set_device_id.add(device.get("device_id"))
                    lst_suggest_device.append(
                        self.__build_value__(value=device, suggest=True)
                    )
        elif type(origin_data) == dict:
            lst_suggest_device.append(
                self.__build_value__(value=origin_data, suggest=True)
            )
        suggest_data[field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.OTHER,
            value=lst_suggest_device,
        )

    def merge_data(self, target_data, source_data, field_key, is_master_data=False):
        if source_data:
            target_data[field_key] = (
                target_data.get(field_key) if target_data.get(field_key) else []
            )
            set_device_id = set(
                [x.get("device_id") for x in target_data.get(field_key)]
            )
            for device_data in source_data.get("field_value"):
                device = device_data.get("value")
                if device.get("device_id") not in set_device_id:
                    target_data[field_key].append(device)
                    set_device_id.add(device.get("device_id"))

    def validate_merge(self, data, schema_validate_value=None):
        schema_validate_value = {
            "changeable": fields.Boolean(default=True, missing=True, allow_none=False),
            "suggest": fields.Boolean(default=True, missing=True, allow_none=False),
            "value": fields.Nested(DeviceSchema),
            "status": fields.Int(default=None, allow_none=True),
            "predict": fields.Dict(allow_none=True),
        }
        field_value = data.get("field_value", [])
        tmp_field_value = []
        for value in field_value:
            generated_schema_value = Schema.from_dict(schema_validate_value)
            try:
                valid_value = generated_schema_value().load(value)
                tmp_field_value.append(valid_value)
            except ValidationError as ex:
                print(
                    "MergeDevices:: validation value error: {}".format(ex)
                )
        data["field_value"] = tmp_field_value
        rules = {
            "display_type": fields.Str(
                validate=validate.OneOf([x.value for x in DisplayType])
            ),
            "displayable": fields.Boolean(),
            "editable": fields.Boolean(),
            "field_property": fields.Int(),
            "group": fields.Str(),
            "mergeable": fields.Boolean(),
            "order": fields.Int(),
            "tooltip_i18n": fields.Str(allow_none=True, missing=None, default=None),
            "translate_key": fields.Str(allow_none=True, missing=None, default=None),
            "field_value": fields.List(
                fields.Nested(Schema.from_dict(schema_validate_value))
            ),
        }

        generated_schema = Schema.from_dict(rules)
        return generated_schema().load(data)
