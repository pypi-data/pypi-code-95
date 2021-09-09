from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeSocialName(BaseMerge):
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
        predict=None
    ):
        lst_social = []
        for social in profile_data:
            _id = social.get("id")
            _name = social.get("name")
            _social_id = social.get("social_id")
            unique_suggest_value = "{}:{}".format(_id, _name)
            suggest = True if unique_suggest_value not in set_unique_suggest_values else False
            lst_social.append(
                self.__build_value__(value=social, suggest=suggest, changealbe=False)
            )
            set_unique_suggest_values.add(unique_suggest_value)

        suggest_data[field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_social,
        )

    def set_filter_value(self, suggest_filter_data: set, profile_data):
        for social in profile_data:
            if social.get("name"):
                suggest_filter_data.add(social.get("name"))

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
        pass

    def merge_data(self, target_data, source_data, field_key, is_master_data=False):
        if source_data:
            lst_social_name = target_data.get(field_key, [])
            set_social_name = set()
            for source_social in source_data.get('field_value'):
                _id = source_social.get("id")
                _name = source_social.get("name")
                _social_id = source_social.get("social_id")
                unique_suggest_value = "{}:{}".format(_id, _name)
                if unique_suggest_value not in set_social_name:
                    lst_social_name.append(source_social)
                    set_social_name.add(unique_suggest_value)
            target_data[field_key] = lst_social_name
