from lumipy.navigation.atlas import Atlas
from lumipy.navigation.field_metadata import FieldMetadata
from lumipy.navigation.provider_metadata import ProviderMetadata
from lumipy.client import Client
from typing import Optional, List
from lumipy.common.string_utils import random_globe
from pandas import DataFrame


def query_provider_metadata(client: Client) -> DataFrame:
    """Query luminesce for metadata on the available providers.

    Args:
        client (Client): lumipy client to query with.

    Returns:
        DataFrame: pandas dataframe containing query result.
    """

    return client.query_and_fetch("""
        select
          svc.[MqUserName], svc.[Description], svc.[Type], 
          svc.[Category], svc.[Client], 
          svc.[DocumentationLink], svc.[LastPingAt], svc.[LicenceCode], fld.[FieldName], fld.[TableName], 
          fld.[Source], fld.[DataType], fld.[FieldType], fld.[Description] as [Description_fld], fld.[IsMain], 
          fld.[IsPrimaryKey], fld.[ParamDefaultValue], fld.[TableParamColumns] 
        from
          Sys.Field as fld 
        left join
          Sys.Service as svc
         on
          ((svc.[Name] = fld.[TableName]) 
          and (svc.[Type] = 'DataProvider')) 
          and (fld.[FieldName] is not null)          
    """)


def build_provider_metadata_objects(df: DataFrame, client: Client) -> List[ProviderMetadata]:
    """Build a list of provider metadata objects from the queried metadata rows.

    Args:
        df (DataFrame): dataframe containing the queried luminesce provider metadata.
        client (Client): the client to attach to the provider metadata objects.

    Returns:
        List[ProviderMetadata]: list of provider metadata objects to build the atlas with.
    """

    provider_descriptions = []
    for p, p_df in df.groupby('TableName'):

        fields = [FieldMetadata.from_row(row) for _, row in p_df.iterrows()]

        p_row = p_df.iloc[0]
        provider = ProviderMetadata(
            table_name=p_row.TableName,
            description=p_row.Description,
            provider_type=p_row.Type,
            category=p_row.Category,
            last_ping_at=p_row.LastPingAt,
            documentation=p_row.DocumentationLink,
            fields=fields,
            client=client
        )

        provider_descriptions.append(provider)
    return provider_descriptions


def get_atlas(secrets: Optional[str] = None, token: Optional[str] = None) -> Atlas:
    """Get luminesce data provider atlas instance.

    Args:
        secrets (Optional[str]): path to secrets file. If not supplied authentication information will be retrieved
        from the environment.
        token (Optional[str]): authentication token.

    Returns:
        Atlas: the atlas instance.
    """

    print("Building atlas... ", end='')

    client = Client(secrets, token)
    at_df = query_provider_metadata(client)
    provider_meta = build_provider_metadata_objects(at_df, client)

    atlas = Atlas(
        provider_meta,
        atlas_type='All available data providers'
    )
    globe = random_globe()

    print(f'done!{globe}')

    return atlas
