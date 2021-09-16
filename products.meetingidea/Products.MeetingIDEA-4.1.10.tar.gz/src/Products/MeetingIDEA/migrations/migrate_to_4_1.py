# -*- coding: utf-8 -*-

from Products.GenericSetup.tool import DEPENDENCY_STRATEGY_NEW
from Products.MeetingCommunes.migrations.migrate_to_4_1 import Migrate_To_4_1 as MCMigrate_To_4_1

import logging

from plone import api

logger = logging.getLogger("MeetingIDEA")


class Migrate_To_4_1(MCMigrate_To_4_1):

    def _migrateInternalCommunicationAttribute(self):
        """Field MeetingConfig.itemGroupInChargeStates was renamed to MeetingConfig.itemGroupsInChargeStates.
           Value reader_groupincharge is now reader_groupsincharge."""
        logger.info("Adapting meetingConfigs...")
        for cfg in self.tool.objectValues("MeetingConfig"):
            used_item_attrs = list(cfg.getUsedItemAttributes())
            if "meetingManagersNotes" not in used_item_attrs:
                used_item_attrs.append("meetingManagersNotes")
            cfg.setUsedItemAttributes(used_item_attrs)
        logger.info("Adapting items...")
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog(meta_type=["MeetingItem"])
        for brain in brains:
            item = brain.getObject()
            if hasattr(item, "internalCommunication"):
                item.setMeetingManagersNotes(item.internalCommunication)
                delattr(item, "internalCommunication")

    def run(self):

        super(Migrate_To_4_1, self).run(extra_omitted=['Products.MeetingIDEA:default'])
        # now MeetingIDEA specific steps
        logger.info("Migrating to MeetingIDEA 4.1...")
        self._migrateInternalCommunicationAttribute()


# The migration function -------------------------------------------------------
def migrate(context):
    """This migration function:

       1) Execute Products.MeetingCommunes migration.
       2) Migrate InternalCommunication attribute
    """
    migrator = Migrate_To_4_1(context)
    migrator.run()
    migrator.finish()
