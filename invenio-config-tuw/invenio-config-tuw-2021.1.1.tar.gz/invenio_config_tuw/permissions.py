# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from flask_principal import RoleNeed
from invenio_rdm_records.services import RDMRecordPermissionPolicy
from invenio_rdm_records.services.generators import (
    IfRestricted,
    RecordOwners,
    SecretLinks,
)
from invenio_records_permissions.generators import (
    Admin,
    AnyUser,
    Disable,
    Generator,
    SuperUser,
    SystemProcess,
)


class TrustedUsers(Generator):
    """Allows users with the "trusted-user" role."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        return [RoleNeed("trusted-user")]


secret_links = {
    "edit": [SecretLinks("edit")],
    "view": [SecretLinks("edit"), SecretLinks("view")],
    "view_record": [SecretLinks("edit"), SecretLinks("view"), SecretLinks("record")],
    "view_files": [SecretLinks("edit"), SecretLinks("view"), SecretLinks("files")],
    "preview": [SecretLinks("edit"), SecretLinks("preview")],
}

owner_if_restricted_record = IfRestricted(
    "record", then_=[RecordOwners()], else_=[AnyUser()]
)

owner_if_restricted_files = IfRestricted(
    "files", then_=[RecordOwners()], else_=[AnyUser()]
)


class TUWRecordPermissionPolicy(RDMRecordPermissionPolicy):
    # note: edit := create a draft from a record (i.e. putting it in edit mode)
    # fmt: off
    # high-level permissions
    can_manage             = [RecordOwners(),             Admin(), SuperUser(), SystemProcess()]                                # noqa
    can_curate             = [RecordOwners(),             Admin(), SuperUser(), SystemProcess()] + secret_links["edit"]         # noqa
    can_preview            = [RecordOwners(),             Admin(), SuperUser(), SystemProcess()] + secret_links["preview"]      # noqa
    can_view               = [RecordOwners(),             Admin(), SuperUser(), SystemProcess()] + secret_links["view"]         # noqa

    # records
    can_search             = [AnyUser(),                  Admin(), SuperUser(), SystemProcess()]                                # noqa
    can_read               = [owner_if_restricted_record, Admin(), SuperUser(), SystemProcess()] + secret_links["view_record"]  # noqa
    can_read_files         = [owner_if_restricted_files,  Admin(), SuperUser(), SystemProcess()] + secret_links["view_files"]   # noqa
    can_create             = [TrustedUsers(),             Admin(), SuperUser(), SystemProcess()]                                # noqa

    # drafts
    can_search_drafts      = [TrustedUsers(),             Admin(), SuperUser(), SystemProcess()]                                # noqa
    can_read_draft         = [                          *can_preview                           ]                                # noqa
    can_update_draft       = [                          *can_curate                            ]                                # noqa
    can_draft_read_files   = [                          *can_preview                           ]                                # noqa
    can_draft_create_files = [                          *can_curate                            ]                                # noqa
    can_draft_update_files = [                          *can_curate                            ]                                # noqa
    can_draft_delete_files = [                          *can_curate                            ]                                # noqa

    # PIDs
    can_pid_reserve        = [                          *can_curate                            ]                                # noqa
    can_pid_delete         = [                          *can_curate                            ]                                # noqa

    # actions
    can_edit               = [                          *can_curate                            ]                                # noqa
    can_delete_draft       = [                          *can_curate                            ]                                # noqa
    can_new_version        = [                          *can_curate                            ]                                # noqa
    can_publish            = [                          *can_curate                            ]                                # noqa
    can_lift_embargo       = [                          *can_manage                            ]                                # noqa

    # disabled (record management in InvenioRDM goes through drafts)
    can_update             = [                           Disable()                             ]                                # noqa
    can_delete             = [                           Disable()                             ]                                # noqa
    can_create_files       = [                           Disable()                             ]                                # noqa
    can_update_files       = [                           Disable()                             ]                                # noqa
    can_delete_files       = [                           Disable()                             ]                                # noqa
    # fmt: on
