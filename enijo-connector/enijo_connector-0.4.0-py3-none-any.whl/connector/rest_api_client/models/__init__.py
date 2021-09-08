""" Contains all the data models used in inputs/outputs """

from .access_information import AccessInformation
from .access_information_embargo import AccessInformationEmbargo
from .access_information_files import AccessInformationFiles
from .access_information_record import AccessInformationRecord
from .affiliation_identifier import AffiliationIdentifier
from .affiliation_identifier_scheme import AffiliationIdentifierScheme
from .creator_identifier import CreatorIdentifier
from .creator_identifier_scheme import CreatorIdentifierScheme
from .draft_files_create_item import DraftFilesCreateItem
from .draft_files_read import DraftFilesRead
from .draft_files_read_entry import DraftFilesReadEntry
from .draft_files_read_entry_metadata import DraftFilesReadEntryMetadata
from .draft_files_read_entry_status import DraftFilesReadEntryStatus
from .draft_files_read_meta import DraftFilesReadMeta
from .error import Error
from .error_errors_item import ErrorErrorsItem
from .files import Files
from .files_entries import FilesEntries
from .files_entries_additional_property import FilesEntriesAdditionalProperty
from .files_meta import FilesMeta
from .identifier import Identifier
from .metadata import Metadata
from .metadata_creators_item import MetadataCreatorsItem
from .metadata_creators_item_affiliations_item import (
    MetadataCreatorsItemAffiliationsItem,
)
from .metadata_creators_item_person_or_org import MetadataCreatorsItemPersonOrOrg
from .metadata_creators_item_person_or_org_type import (
    MetadataCreatorsItemPersonOrOrgType,
)
from .metadata_resource_type import MetadataResourceType
from .record_new import RecordNew
from .record_new_files import RecordNewFiles
from .record_read import RecordRead
from .record_read_ext import RecordReadExt
from .record_read_links import RecordReadLinks
from .record_read_parent import RecordReadParent
from .record_read_parent_access import RecordReadParentAccess
from .record_read_parent_access_owned_by_item import RecordReadParentAccessOwnedByItem
from .record_read_provenance import RecordReadProvenance
from .record_read_tombstone import RecordReadTombstone
from .record_read_versions import RecordReadVersions
from .resource_type_id import ResourceTypeId
