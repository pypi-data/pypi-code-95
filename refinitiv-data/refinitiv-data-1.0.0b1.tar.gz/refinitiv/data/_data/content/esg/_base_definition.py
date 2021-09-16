from ...delivery import bulk
from .._content_provider import ContentProviderLayer
from .._content_type import ContentType
from ...tools._repr_definition import create_str_definition

package_name_by_content_type = {
    ContentType.ESG_FULL_MEASURES: "esg.full_measures",
    ContentType.ESG_FULL_SCORES: "esg.full_scores",
    ContentType.ESG_STANDARD_MEASURES: "esg.standard_measures",
    ContentType.ESG_STANDARD_SCORES: "esg.standard_scores",
}


def get_package_name(content_type: ContentType):
    package_name = package_name_by_content_type.get(content_type)

    if not package_name:
        raise ValueError(f"Cannot find package_name by content_type={content_type}")

    return package_name


class BaseDefinition(ContentProviderLayer):
    def get_db_data(self):
        """
        Returns a response to the data platform

        Returns
        -------
        Response

        """
        definition = bulk.Definition(
            package_name=get_package_name(self._content_type),
            universe=self._kwargs.get("universe"),
        )
        response = definition.get_db_data()
        return response

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.esg",
            content=f"{{universe='{self._kwargs.get('universe')}', "
            f"start='{self._kwargs.get('start')}', "
            f"end='{self._kwargs.get('end')}', "
            f"closure='{self._kwargs.get('closure')}'}}",
        )


class BaseDefinition(ContentProviderLayer):
    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.esg",
            content=f"{{universe='{self._kwargs.get('universe')}', "
            f"start='{self._kwargs.get('start')}', "
            f"end='{self._kwargs.get('end')}', "
            f"closure='{self._kwargs.get('closure')}'}}",
        )
