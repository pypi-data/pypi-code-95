from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import DISPLAY_TYPE_IS_LIST_TYPE


class MergeDynamic(BaseMerge):
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
        if display_type in DISPLAY_TYPE_IS_LIST_TYPE:
            field_value = []
            if profile_data:
                for row in profile_data:
                    field_value.append(self.__build_value__(value=row, suggest=True))
        else:
            suggest = (
                True
                if profile_data is not None
                and profile_data != ""
                and field_key not in set_suggest_fields
                else False
            )
            field_value = self.__build_value__(value=profile_data, suggest=suggest)
            if suggest:
                set_suggest_fields.add(field_key)
        suggest_data[field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.DYNAMIC,
            value=field_value,
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
        if display_type in DISPLAY_TYPE_IS_LIST_TYPE:
            field_value = []
            if origin_data:
                for row in origin_data:
                    field_value.append(self.__build_value__(value=row, suggest=True))
        else:
            suggest = (
                True
                if origin_data is not None
                and origin_data != ""
                and field_key not in set_suggest_fields
                else False
            )
            field_value = self.__build_value__(value=origin_data, suggest=suggest)
            if suggest:
                set_suggest_fields.add(field_key)
        suggest_data[field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.DYNAMIC,
            value=field_value,
        )

    def merge_data(self, target_data, source_data, field_key, is_master_data=False):
        if source_data:
            if type(source_data.get("field_value")) == list:
                target_data[field_key] = (
                    target_data.get(field_key) if target_data.get(field_key) else []
                )
                set_data = (
                    set(target_data.get(field_key)) if not is_master_data else set()
                )
                for row in source_data.get("field_value"):
                    suggest = row.get("suggest")
                    value = row.get("value")
                    if suggest and value is not None:
                        set_data.add(value)
                target_data[field_key] = list(set_data)
            else:
                suggest = source_data.get("field_value").get("suggest")
                value = source_data.get("field_value").get("value")
                if suggest and value is not None:
                    target_data[field_key] = value


if __name__ == "__main__":
    old, new = MergeDynamic().get_updated_data(data={
                'display_type': 'date_picker',
                'key': '_dyn_truong_test_datepicker_ddmm_1616574483327',
                'field_key': '_dyn_truong_test_datepicker_ddmm_1616574483327',
                'translate_key': '',
                'add': [],
                'format': 'dd/mm',
                'change': [
                    {
                        'from': '2099-09-11T00:00:00.000000Z',
                        'to': '2099-08-09T00:00:00.000000Z'
                    }
                ],
                'field_property': 3,
                'field_name': 'Truong_test_datepicker_DDMM',
                'remove': []
            })
    print('old: {}, new: {}'.format(old, new))
