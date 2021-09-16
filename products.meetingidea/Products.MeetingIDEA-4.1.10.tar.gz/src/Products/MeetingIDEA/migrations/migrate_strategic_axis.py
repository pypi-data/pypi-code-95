# -*- coding: utf-8 -*-

import logging

from Products.PloneMeeting.migrations import Migrator
from Products.ZCatalog.ProgressHandler import ZLogHandler

logger = logging.getLogger('MeetingIDEA')


# The migration class ----------------------------------------------------------
class MigrateStrategicAxis(Migrator):

    def _migrate_strategic_axis_to_classifier_field(self):
        logger.info('Migrating Strategic Axis to Classifier field')

        logger.info("Adapting meetingConfigs...")
        for cfg in self.tool.objectValues("MeetingConfig"):
            used_item_attrs = list(cfg.getUsedItemAttributes())
            if "internalCommunication" in used_item_attrs:
                used_item_attrs.remove("internalCommunication")
            if "strategicAxis" in used_item_attrs:
                used_item_attrs.remove("strategicAxis")
            cfg.setUsedItemAttributes(used_item_attrs)

        logger.info("Adapting items...")
        pghandler = ZLogHandler(steps=10)
        brains = self.portal.reference_catalog(relationship='ItemStrategicAxis')
        pghandler.init('Updating field MeetingItem.strategicAxis...', len(brains))
        pghandler.info('Updating field MeetingItem.strategicAxis...')
        for i, brain in enumerate(brains):
            pghandler.report(i)
            relation = brain.getObject()
            item = relation.getSourceObject()
            classifier = relation.getTargetObject()
            item.setClassifier(classifier.getId())
            item.reindexObject(idxs=['getRawClassifier'])

        pghandler.finish()
        logger.info('Done migrating Strategic Axis to Classifier field')

    def run(self, step=None):
        self._migrate_strategic_axis_to_classifier_field()


# The migrate function -------------------------------------------------------
def migrate(context):
    """This upgrade-step function will:
       add somes searches, defines in adapter, for all Meeting Config
    """
    migrator = MigrateStrategicAxis(context)
    migrator.run()
    migrator.finish()
